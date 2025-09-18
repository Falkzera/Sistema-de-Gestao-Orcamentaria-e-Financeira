import time
import os
import subprocess
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

def is_local():
    """
    Verifica se a aplicação está rodando localmente (modo desenvolvedor)
    """
    try:
        # Verifica variáveis de ambiente que indicam desenvolvimento
        is_dev_env = (
            os.getenv('STREAMLIT_SERVER_PORT') is not None or
            os.getenv('STREAMLIT_DEV_MODE') == 'true' or
            'localhost' in str(os.getenv('STREAMLIT_SERVER_ADDRESS', '')) or
            '127.0.0.1' in str(os.getenv('STREAMLIT_SERVER_ADDRESS', ''))
        )
        
        # Verifica se está rodando em porta de desenvolvimento (8501 é padrão do Streamlit)
        dev_port = os.getenv('STREAMLIT_SERVER_PORT', '8501')
        
        return is_dev_env or dev_port == '8501'
        
    except Exception:
        return False

def get_chrome_version():
    """
    Detecta a versão do Chrome/Chromium instalada no sistema
    """
    print("🔧 [DEBUG] Detectando versão do Chrome...")
    
    try:
        # Detecta o sistema operacional
        import platform
        system = platform.system().lower()
        print(f"🔧 [DEBUG] Sistema operacional: {system}")
        
        commands = []
        
        if system == "windows":
            # Windows - tenta diferentes localizações do Chrome
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
                "chrome.exe"  # Se estiver no PATH
            ]
            
            for path in chrome_paths:
                 if os.path.exists(path) or path == "chrome.exe":
                     commands.append([path, "--version"])
                    
            # Também tenta via registro do Windows
            try:
                import winreg
                print("🔧 [DEBUG] Tentando detectar via registro do Windows...")
                
                # Tenta diferentes chaves do registro
                registry_paths = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Google\Chrome\BLBeacon"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Google\Chrome\BLBeacon"),
                ]
                
                for hkey, subkey in registry_paths:
                    try:
                        with winreg.OpenKey(hkey, subkey) as key:
                            version, _ = winreg.QueryValueEx(key, "version")
                            print(f"✅ [DEBUG] Versão encontrada no registro: {version}")
                            
                            # Extrai versão major
                            version_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', version)
                            if version_match:
                                major_version = version_match.group(1)
                                print(f"✅ [DEBUG] Versão detectada via registro: {version} (major: {major_version})")
                                return version, major_version
                                
                    except (FileNotFoundError, OSError, winreg.error):
                        continue
                        
            except ImportError:
                print("🔧 [DEBUG] winreg não disponível")
                
        else:
            # Linux/Cloud (Chromium) - prioriza o caminho específico do Streamlit Cloud
            commands = [
                ["/usr/bin/chromium", "--version"],  # Caminho específico do Streamlit Cloud
                ["/usr/bin/chromium-browser", "--version"],
                ["chromium", "--version"],
                ["chromium-browser", "--version"],
                ["google-chrome", "--version"],
                ["google-chrome-stable", "--version"],
            ]
            
            # Estratégia adicional: verifica se existe o binário no caminho específico
            if os.path.exists("/usr/bin/chromium"):
                print("🔧 [DEBUG] Chromium encontrado em /usr/bin/chromium (Streamlit Cloud)")
                try:
                    # Força detecção no caminho específico do Streamlit Cloud
                    result = subprocess.run(["/usr/bin/chromium", "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version_output = result.stdout.strip()
                        print(f"🔧 [DEBUG] Versão do Chromium no Cloud: {version_output}")
                        
                        # Extrai versão específica para Chromium 120.x
                        version_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', version_output)
                        if version_match:
                            version = version_match.group(0)
                            major_version = version_match.group(1)
                            print(f"✅ [DEBUG] Versão Chromium Cloud detectada: {version} (major: {major_version})")
                            return version, major_version
                except Exception as e:
                    print(f"⚠️ [DEBUG] Erro ao detectar Chromium no Cloud: {str(e)}")
                    pass
        
        # Tenta executar comandos
        for cmd in commands:
            try:
                print(f"🔧 [DEBUG] Tentando comando: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_output = result.stdout.strip()
                    print(f"🔧 [DEBUG] Saída do comando: {version_output}")
                    
                    # Extrai o número da versão usando regex
                    version_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', version_output)
                    if version_match:
                        version = version_match.group(0)
                        major_version = version_match.group(1)
                        print(f"✅ [DEBUG] Versão detectada: {version} (major: {major_version})")
                        return version, major_version
                        
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
                print(f"🔧 [DEBUG] Comando {cmd[0]} falhou: {str(e)}")
                continue
        
        print("⚠️ [DEBUG] Não foi possível detectar a versão do Chrome")
        return None, None
        
    except Exception as e:
        print(f"❌ [DEBUG] Erro ao detectar versão do Chrome: {str(e)}")
        return None, None

def get_compatible_chromedriver_version(chrome_version):
    """
    Retorna a versão compatível do ChromeDriver baseada na versão do Chrome
    """
    if not chrome_version:
        return None
    
    try:
        major_version = int(chrome_version.split('.')[0])
        print(f"🔧 [DEBUG] Versão major do Chrome: {major_version}")
        
        # Mapeamento de versões compatíveis (baseado na documentação oficial)
        version_mapping = {
            140: "140.0.7339.128",  # Versão mais recente
            139: "139.0.7302.122",
            138: "138.0.7262.94",
            137: "137.0.7225.93",
            136: "136.0.7188.102",
            135: "135.0.7151.116",
            134: "134.0.7114.102",
            133: "133.0.7077.126",
            132: "132.0.7040.122",
            131: "131.0.7003.120",
            130: "130.0.6966.116",
            129: "129.0.6929.110",
            128: "128.0.6892.102",
            127: "127.0.6855.122",
            126: "126.0.6818.119",
            125: "125.0.6781.107",
            124: "124.0.6744.117",
            123: "123.0.6707.116",
            122: "122.0.6670.129",
            121: "121.0.6633.119",
            120: "120.0.6099.109",
            119: "119.0.6045.105", 
            118: "118.0.5993.70",
            117: "117.0.5938.92",
            116: "116.0.5845.96",
            115: "115.0.5790.102",
            114: "114.0.5735.90",
        }
        
        compatible_version = version_mapping.get(major_version)
        if compatible_version:
            print(f"✅ [DEBUG] Versão compatível do ChromeDriver: {compatible_version}")
            return compatible_version
        else:
            print(f"⚠️ [DEBUG] Versão {major_version} não mapeada, usando automática")
            return None
            
    except Exception as e:
        print(f"❌ [DEBUG] Erro ao determinar versão compatível: {str(e)}")
        return None

# def chrome():
#     """Configura e retorna uma instância do Chrome WebDriver otimizada"""
#     print("🔧 [DEBUG] Iniciando configuração do Chrome...")
    
#     try:
#         # Configurações do Chrome
#         print("🔧 [DEBUG] Configurando opções do Chrome...")
#         options = Options()
#         options.add_argument("--headless")  # Modo headless ativado
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-plugins")
#         options.add_argument("--disable-images")
#         options.add_argument("--disable-background-timer-throttling")
#         options.add_argument("--disable-backgrounding-occluded-windows")
#         options.add_argument("--disable-renderer-backgrounding")
#         options.add_argument("--disable-features=TranslateUI")
#         options.add_argument("--disable-ipc-flooding-protection")
#         options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
#         print("✅ [DEBUG] Opções do Chrome configuradas")
        
#         # Configuração do serviço usando webdriver-manager
#         print("🔧 [DEBUG] Configurando serviço do ChromeDriver com webdriver-manager...")
#         try:
#             # Usa o webdriver-manager para baixar automaticamente a versão correta
#             print("🔧 [DEBUG] Baixando/verificando ChromeDriver compatível...")
#             driver_path = ChromeDriverManager().install()
#             print(f"✅ [DEBUG] ChromeDriver encontrado/baixado: {driver_path}")
#             service = Service(driver_path)
#         except Exception as e:
#             print(f"⚠️ [DEBUG] Erro com webdriver-manager: {str(e)}")
#             # Fallback para chromedriver local se existir
#             chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
#             if os.path.exists(chromedriver_path):
#                 print(f"🔧 [DEBUG] Usando ChromeDriver local como fallback: {chromedriver_path}")
#                 service = Service(chromedriver_path)
#             else:
#                 print("⚠️ [DEBUG] Usando serviço padrão como último recurso")
#                 service = Service()
        
#         print("✅ [DEBUG] Serviço configurado")
        
#         # Cria o driver
#         print("🔧 [DEBUG] Criando instância do WebDriver...")
#         driver = webdriver.Chrome(service=service, options=options)
#         print("✅ [DEBUG] WebDriver criado com sucesso")
        
#         # Configurações adicionais
#         print("🔧 [DEBUG] Aplicando configurações adicionais...")
#         driver.set_page_load_timeout(30)
#         driver.implicitly_wait(10)
#         print("✅ [DEBUG] Configurações aplicadas")
        
#         return driver

def chrome():
    """Configura e retorna uma instância do Chrome WebDriver otimizada"""
    print("🚀 [DEBUG] Iniciando configuração do Chrome WebDriver...")
    
    # Configurações de opções do Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    
    # Detecta se está no ambiente local ou cloud
    local_env = is_local()
    print(f"🔧 [DEBUG] Ambiente detectado: {'Local' if local_env else 'Streamlit Cloud'}")
    
    # Detecta versão do Chrome instalada
    chrome_version, chrome_major = get_chrome_version()
    compatible_driver_version = get_compatible_chromedriver_version(chrome_version)
    
    driver = None
    
    try:
        if not local_env:
            # Configuração específica para Streamlit Cloud
            print("☁️ [DEBUG] Configurando para Streamlit Cloud...")
            print(f"🔧 [DEBUG] Chromium detectado: versão {chrome_version if chrome_version else 'não detectada'}")
            
            # Estratégia 1: Força versão específica compatível com Chromium 120
            try:
                if chrome_major and int(chrome_major) >= 120:
                    # Para Chromium 120+, força versão específica do ChromeDriver
                    target_version = "120.0.6099.109"  # Versão compatível com Chromium 120
                    print(f"🔧 [DEBUG] Forçando ChromeDriver versão {target_version} para Chromium {chrome_major}")
                    driver_path = ChromeDriverManager(version=target_version).install()
                else:
                    # Fallback para versão automática se não conseguir detectar
                    print("🔧 [DEBUG] Usando versão automática como fallback...")
                    driver_path = ChromeDriverManager().install()
                
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                print("✅ [DEBUG] ChromeDriver específico configurado com sucesso!")
                return driver
                
            except Exception as e:
                print(f"⚠️ [DEBUG] Falha com versão específica: {str(e)}")
                
                # Estratégia 2: Tenta versões conhecidas compatíveis
                compatible_versions = ["120.0.6099.109", "119.0.6045.105", "118.0.5993.70"]
                for version in compatible_versions:
                    try:
                        print(f"🔧 [DEBUG] Tentando ChromeDriver versão {version}...")
                        driver_path = ChromeDriverManager(version=version).install()
                        service = Service(driver_path)
                        driver = webdriver.Chrome(service=service, options=options)
                        print(f"✅ [DEBUG] ChromeDriver versão {version} funcionou!")
                        return driver
                    except Exception as ve:
                        print(f"⚠️ [DEBUG] Versão {version} falhou: {str(ve)}")
                        continue
                
                # Estratégia 3: Configuração de emergência
                print("🆘 [DEBUG] Tentando configuração de emergência...")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-images")
                options.add_argument("--disable-javascript")
                
                try:
                    driver = webdriver.Chrome(options=options)
                    print("✅ [DEBUG] Configuração de emergência funcionou!")
                    return driver
                except Exception as e4:
                    print(f"❌ [DEBUG] Configuração de emergência falhou: {str(e4)}")
                    raise e4
        
        else:
            # Configuração para ambiente local
            print("🏠 [DEBUG] Configurando para ambiente local...")
            
            # Estratégia 1: Detecta versão mas usa ChromeDriverManager automático
            if compatible_driver_version:
                print(f"🔧 [DEBUG] Versão detectada: {compatible_driver_version}, usando ChromeDriverManager automático...")
            
            # Estratégia 2: Tenta usar driver local primeiro
            if os.path.exists("chromedriver.exe"):
                try:
                    print("🔧 [DEBUG] Usando ChromeDriver local...")
                    service = Service("chromedriver.exe")
                    driver = webdriver.Chrome(service=service, options=options)
                    print("✅ [DEBUG] ChromeDriver local configurado com sucesso!")
                    return driver
                except Exception as e:
                    print(f"⚠️ [DEBUG] Falha com driver local: {str(e)}")
            
            # Estratégia 3: Usa ChromeDriverManager para ambiente local
            try:
                print("🔧 [DEBUG] Baixando ChromeDriver via ChromeDriverManager...")
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                print("✅ [DEBUG] ChromeDriver baixado e configurado com sucesso!")
                return driver
            except Exception as e:
                print(f"❌ [DEBUG] Falha com ChromeDriverManager: {str(e)}")
                raise e
                
    except Exception as e:
        print(f"❌ [DEBUG] Erro crítico na configuração do Chrome: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise e

    # except Exception as e:
    #     print(f"❌ [DEBUG] ERRO na configuração do Chrome: {str(e)}")
    #     raise e

class SEILogin:
    def __init__(self, base_url="https://sei.al.gov.br"):
        self.base_url = base_url
        self.driver = None
    
    def setup_driver(self):
        """Configura o driver do Chrome usando a função chrome() otimizada"""
        print("🔧 [DEBUG] Iniciando setup_driver...")
        try:
            self.driver = chrome()
            print("✅ [DEBUG] Driver configurado com sucesso no setup_driver")
            return self.driver
        except Exception as e:
            print(f"❌ [DEBUG] ERRO no setup_driver: {str(e)}")
            raise e
    
    def login(self, cpf, senha, unidade="GOVERNANCA"):
        """Realiza o login no sistema SEI de forma simplificada"""
        print(f"🔧 [DEBUG] Iniciando login para usuário: {cpf}")
        print(f"🔧 [DEBUG] Unidade: {unidade}")
        print(f"🔧 [DEBUG] URL base: {self.base_url}")
        
        try:
            # Configura o driver
            print("🔧 [DEBUG] Configurando driver...")
            self.setup_driver()
            print("✅ [DEBUG] Driver configurado com sucesso")
            
            # Navega para a página de login
            print(f"🔧 [DEBUG] Navegando para: {self.base_url}")
            try:
                self.driver.get(self.base_url)
                print("✅ [DEBUG] Navegação bem-sucedida")
            except TimeoutException:
                print("❌ [DEBUG] TIMEOUT: Página demorou muito para carregar")
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Timeout: Página demorou muito para carregar"
                }
            except Exception as e:
                print(f"❌ [DEBUG] ERRO na navegação: {str(e)}")
                self.close()
                return {
                    "sucesso": False,
                    "erro": f"Erro na navegação: {str(e)}"
                }
            
            # Aguarda a página carregar
            print("🔧 [DEBUG] Aguardando página carregar...")
            wait = WebDriverWait(self.driver, 30)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
                print("✅ [DEBUG] Formulário encontrado na página")
            except TimeoutException:
                print("❌ [DEBUG] TIMEOUT: Formulário não encontrado")
                print(f"🔧 [DEBUG] URL atual: {self.driver.current_url}")
                print(f"🔧 [DEBUG] Título da página: {self.driver.title}")
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Timeout: Formulário não encontrado na página"
                }
            
            print("🔧 [DEBUG] Aguardando 2 segundos...")
            time.sleep(2)
            print(f"🔧 [DEBUG] URL atual após carregamento: {self.driver.current_url}")
            
            # Preenche campo de usuário
            print("🔧 [DEBUG] Procurando campo de usuário...")
            try:
                campo_usuario = wait.until(EC.element_to_be_clickable((By.ID, "txtUsuario")))
                print("✅ [DEBUG] Campo de usuário encontrado")
                campo_usuario.clear()
                campo_usuario.send_keys(cpf)
                print(f"✅ [DEBUG] Usuário '{cpf}' preenchido")
            except TimeoutException:
                print("❌ [DEBUG] TIMEOUT: Campo de usuário não encontrado")
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Campo de usuário não encontrado"
                }
            except Exception as e:
                print(f"❌ [DEBUG] ERRO ao preencher usuário: {str(e)}")
                self.close()
                return {
                    "sucesso": False,
                    "erro": f"Erro ao preencher usuário: {str(e)}"
                }
            
            # Preenche campo de senha
            print("🔧 [DEBUG] Procurando campo de senha...")
            try:
                campo_senha = wait.until(EC.element_to_be_clickable((By.ID, "pwdSenha")))
                print("✅ [DEBUG] Campo de senha encontrado")
                campo_senha.clear()
                campo_senha.send_keys(senha)
                print("✅ [DEBUG] Senha preenchida")
            except TimeoutException:
                print("❌ [DEBUG] TIMEOUT: Campo de senha não encontrado")
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Campo de senha não encontrado"
                }
            except Exception as e:
                print(f"❌ [DEBUG] ERRO ao preencher senha: {str(e)}")
                self.close()
                return {
                    "sucesso": False,
                    "erro": f"Erro ao preencher senha: {str(e)}"
                }
            
            # Seleciona unidade
            print(f"🔧 [DEBUG] Procurando campo de unidade para selecionar: {unidade}")
            try:
                select_unidade = wait.until(EC.element_to_be_clickable((By.ID, "selOrgao")))
                print("✅ [DEBUG] Campo de unidade encontrado")
                select_obj = Select(select_unidade)
                
                # Lista todas as opções disponíveis para debug
                opcoes = [option.text for option in select_obj.options]
                print(f"🔧 [DEBUG] Opções disponíveis: {opcoes}")
                
                # Procura pela unidade
                unidade_encontrada = False
                for option in select_obj.options:
                    if unidade.upper() in option.text.upper():
                        select_obj.select_by_value(option.get_attribute("value"))
                        unidade_encontrada = True
                        print(f"✅ [DEBUG] Unidade '{unidade}' selecionada")
                        break
                
                if not unidade_encontrada:
                    print(f"❌ [DEBUG] Unidade '{unidade}' não encontrada nas opções")
                    self.close()
                    return {
                        "sucesso": False,
                        "erro": f"Não foi possível selecionar a unidade '{unidade}'"
                    }
            except TimeoutException:
                print("❌ [DEBUG] TIMEOUT: Campo de unidade não encontrado")
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Campo de unidade não encontrado"
                }
            except Exception as e:
                print(f"❌ [DEBUG] ERRO ao selecionar unidade: {str(e)}")
                self.close()
                return {
                    "sucesso": False,
                    "erro": f"Erro ao selecionar unidade '{unidade}': {str(e)}"
                }
            
            # Submete o formulário
            print("🔧 [DEBUG] Procurando botão de login...")
            try:
                botao_login = wait.until(EC.element_to_be_clickable((By.ID, "sbmAcessar")))
                print("✅ [DEBUG] Botão de login encontrado")
                botao_login.click()
                print("✅ [DEBUG] Botão de login clicado")
            except TimeoutException:
                print("❌ [DEBUG] TIMEOUT: Botão de login não encontrado")
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Botão de login não encontrado"
                }
            except Exception as e:
                print(f"❌ [DEBUG] ERRO ao clicar no botão de login: {str(e)}")
                self.close()
                return {
                    "sucesso": False,
                    "erro": f"Não foi possível submeter o formulário: {str(e)}"
                }
            
            # Aguarda o redirecionamento após login
            print("🔧 [DEBUG] Aguardando redirecionamento após login...")
            time.sleep(3)
            
            # Verifica se há alerta de usuário/senha inválida
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"🔧 [DEBUG] Alerta detectado: {alert_text}")
                alert.accept()
                
                if "Usuário ou Senha Inválida" in alert_text or "usuário ou senha" in alert_text.lower():
                    print("❌ [DEBUG] Login falhou - Usuário ou Senha Inválida")
                    self.close()
                    return {
                        "sucesso": False,
                        "erro": "Usuário ou Senha Inválida"
                    }
                else:
                    print(f"❌ [DEBUG] Login falhou - Erro de autenticação: {alert_text}")
                    self.close()
                    return {
                        "sucesso": False,
                        "erro": f"Erro de autenticação: {alert_text}"
                    }
            except:
                # Não há alerta, continua verificação normal
                print("🔧 [DEBUG] Nenhum alerta detectado, continuando verificação...")
                pass
            
            # Verifica se o login foi bem-sucedido
            url_atual = self.driver.current_url
            print(f"🔧 [DEBUG] URL atual após login: {url_atual}")
            print(f"🔧 [DEBUG] Título da página: {self.driver.title}")
            
            if "controlador.php" in url_atual or "principal.php" in url_atual:
                print("✅ [DEBUG] Login realizado com sucesso!")
                return {
                    "sucesso": True,
                    "mensagem": "Login realizado com sucesso!"
                }
            
            # Se chegou até aqui, login falhou
            print("❌ [DEBUG] Login falhou - URL não contém 'controlador.php' ou 'principal.php'")
            # Verifica se há mensagem de erro na página
            try:
                erro_element = self.driver.find_element(By.CLASS_NAME, "infraMensagem")
                mensagem_erro = erro_element.text
                print(f"🔧 [DEBUG] Mensagem de erro encontrada: {mensagem_erro}")
            except Exception as e:
                mensagem_erro = "Login falhou - credenciais inválidas ou erro no sistema"
                print("🔧 [DEBUG] Nenhuma mensagem de erro específica encontrada")
            
            return {
                "sucesso": False,
                "erro": mensagem_erro
            }
                    
        except TimeoutException:
            self.close()
            return {
                "sucesso": False,
                "erro": "Timeout: Página demorou muito para carregar"
            }
        except UnexpectedAlertPresentException:
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                
                if "Usuário ou Senha Inválida" in alert_text or "usuário ou senha" in alert_text.lower():
                    self.close()
                    return {
                        "sucesso": False,
                        "erro": "Usuário ou Senha Inválida"
                    }
                else:
                    self.close()
                    return {
                        "sucesso": False,
                        "erro": f"Erro de autenticação: {alert_text}"
                    }
            except:
                self.close()
                return {
                    "sucesso": False,
                    "erro": "Usuário ou Senha Inválida"
                }
        except Exception as e:
            # Erro geral
            print(f"❌ [DEBUG] ERRO GERAL no método login: {str(e)}")
            print(f"🔧 [DEBUG] Tipo do erro: {type(e).__name__}")
            self.close()
            return {
                "sucesso": False,
                "erro": f"Erro durante o login: {str(e)}"
            }
    
    def close(self):
        """Fecha o navegador"""
        print("🔧 [DEBUG] Iniciando fechamento do driver...")
        if hasattr(self, 'driver') and self.driver:
            try:
                print("🔧 [DEBUG] Fechando driver...")
                self.driver.quit()
                print("✅ [DEBUG] Driver fechado com sucesso")
            except Exception as e:
                print(f"⚠️ [DEBUG] Erro ao fechar driver: {str(e)}")
                pass
            finally:
                self.driver = None
                print("🔧 [DEBUG] Referência do driver removida")
        else:
            print("🔧 [DEBUG] Nenhum driver para fechar")
    
    def __del__(self):
        """Destrutor - garante que o driver seja fechado"""
        print("🔧 [DEBUG] Destrutor chamado - fechando driver...")
        self.close()