import requests
import xml.etree.ElementTree as ET
import subprocess
from tkinter import Tk, Label, Entry, Button, Checkbutton, IntVar, StringVar, DISABLED, NORMAL, messagebox
import os
def processar_xml(xml_content, alteracoes, status_label):
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    ET.register_namespace('', ns['nfe'])
    root = ET.fromstring(xml_content)

    if 'CEP' in alteracoes:
        for elem in root.findall('.//nfe:dest/nfe:enderDest/nfe:CEP', ns):
            elem.text = alteracoes['CEP']
    if 'xMun' in alteracoes:
        for elem in root.findall('.//nfe:dest/nfe:enderDest/nfe:xMun', ns):
            elem.text = alteracoes['xMun']
    if 'UF' in alteracoes:
        for elem in root.findall('.//nfe:dest/nfe:enderDest/nfe:UF', ns):
            elem.text = alteracoes['UF']

    xml_modificado_str = ET.tostring(root, encoding='unicode')

    #parte que gera um xml
    #with open('xml_modificado.txt', 'w', encoding='utf-8') as f:
     #   f.write(xml_modificado_str)

    gerar_json_e_salvar_txt(xml_modificado_str)

    status_label.set("Documento salvo com sucesso!")

def gerar_json_e_salvar_txt(xml_modificado_str):
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    root = ET.fromstring(xml_modificado_str)

    nNF = root.find('.//nfe:infNFe/nfe:ide/nfe:nNF', ns)
    numero = nNF.text if nNF is not None else ""

    infNFe = root.find('.//nfe:infNFe', ns)
    chave = infNFe.attrib.get('Id', '').replace('NFe', '') if infNFe is not None else "arquivo"

    xml_escapado = xml_modificado_str.replace('"', r'\"')

    json_str = (
        '{\n'
        f'    "operacao": "",\n'
        f'    "numero": "{numero}",\n'
        f'    "nf": "{chave}",\n'
        f'    "xml": "{xml_escapado}"\n'
        '}'
    )

    nome_arquivo = f"{chave}.txt"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(json_str)

    print(f"Arquivo salvo como {nome_arquivo}")

    # Abre no bloco de notas
    subprocess.Popen(['notepad.exe', nome_arquivo])

def buscar_pedido(numero_pedido):
    url = os.getenv("API_URL"),{numero_pedido}
    response = requests.get(url, auth=(os.getenv("API_USER"), os.getenv("API_PASS")))

    if response.status_code == 200:
        dados = response.json()
        if isinstance(dados, list) and len(dados) > 0:
            pedido = dados[0]
            entregas = pedido.get('entregas', [])
            if entregas and len(entregas) > 0:
                notas_fiscais = entregas[0].get('notas_fiscais', [])
                if notas_fiscais and len(notas_fiscais) > 0:
                    xml_content = notas_fiscais[0].get('xml', '')
                    if xml_content:
                        abrir_tela_edicao(xml_content)
                        return
    messagebox.showerror("Erro", "Erro ao carregar o pedido ou XML não encontrado.")

def abrir_tela_pedido():
    def ao_confirmar():
        numero = entry_pedido.get()
        if not numero.strip():
            messagebox.showwarning("Atenção", "Informe o número do pedido.")
            return
        root.destroy()
        buscar_pedido(numero)

    root = Tk()
    root.title("Consultar Pedido")

    Label(root, text="Informe o número do pedido:", font=("Arial", 12)).pack(pady=10)
    entry_pedido = Entry(root, width=30)
    entry_pedido.pack(padx=10, pady=5)

    Button(root, text="Carregar Pedido", bg="#2196F3", fg="white", command=ao_confirmar).pack(pady=15)

    root.mainloop()

def abrir_tela_edicao(xml_content):
    root = Tk()
    root.title("Editor de XML")

    status = StringVar()
    status.set("Pedido carregado com sucesso.")

    def atualizar_campos():
        entry_cep.config(state=NORMAL if var_cep.get() else DISABLED)
        entry_xmun.config(state=NORMAL if var_xmun.get() else DISABLED)
        entry_uf.config(state=NORMAL if var_uf.get() else DISABLED)

    def ao_clicar():
        alteracoes = {}
        if var_cep.get():
            alteracoes['CEP'] = entry_cep.get()
        if var_xmun.get():
            alteracoes['xMun'] = entry_xmun.get()
        if var_uf.get():
            alteracoes['UF'] = entry_uf.get()

        if not alteracoes:
            status.set("Selecione pelo menos um campo para alterar.")
            return

        processar_xml(xml_content, alteracoes, status)

    Label(root, text="Marque e altere os campos desejados:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

    var_cep = IntVar()
    var_xmun = IntVar()
    var_uf = IntVar()

    Checkbutton(root, text="CEP", variable=var_cep, command=atualizar_campos).grid(row=1, column=0, sticky='w', padx=10)
    entry_cep = Entry(root, width=30, state=DISABLED)
    entry_cep.grid(row=1, column=1, padx=10, pady=5)

    Checkbutton(root, text="xMun", variable=var_xmun, command=atualizar_campos).grid(row=2, column=0, sticky='w', padx=10)
    entry_xmun = Entry(root, width=30, state=DISABLED)
    entry_xmun.grid(row=2, column=1, padx=10, pady=5)

    Checkbutton(root, text="UF", variable=var_uf, command=atualizar_campos).grid(row=3, column=0, sticky='w', padx=10)
    entry_uf = Entry(root, width=30, state=DISABLED)
    entry_uf.grid(row=3, column=1, padx=10, pady=5)

    Button(root, text="Salvar Documento Modificado", bg="#4CAF50", fg="white", command=ao_clicar).grid(row=4, column=0, columnspan=2, pady=15)

    Label(root, textvariable=status, fg="blue", font=("Arial", 10)).grid(row=5, column=0, columnspan=2, pady=5)

    root.mainloop()

# importa as credenciais da configuração do ambiente
USUARIO = os.getenv("API_USER")
SENHA = os.getenv("API_PASS")
URL_BASE = os.getenv("API_URL")


if not USUARIO or not SENHA or not URL_BASE:
    raise ValueError("API_USER, API_PASS ou API_URL não estão definidos no ambiente.")
if not URL_BASE:
    raise ValueError("A variável de ambiente API_URL não está definida.")


# Inicia
abrir_tela_pedido()


