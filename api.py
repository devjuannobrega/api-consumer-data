import requests
import xml.etree.ElementTree as ET
import subprocess
from tkinter import Tk, Label, Entry, Button, Checkbutton, IntVar, StringVar, DISABLED, NORMAL, messagebox
import os

# Função para processar o XML, aplicar alterações e salvar o resultado
def processar_xml(xml_content, alteracoes, status_label):
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    ET.register_namespace('', ns['nfe'])
    root = ET.fromstring(xml_content)

    # Aplica alterações nos campos selecionados
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
    gerar_json_e_salvar_txt(xml_modificado_str)
    status_label.set("Documento salvo com sucesso!")

# Gera o JSON e salva em arquivo .txt, abre no bloco de notas
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

    subprocess.Popen(['notepad.exe', nome_arquivo])

# Busca o pedido na API e carrega os dados
def buscar_pedido(numero_pedido):
    url = f"{os.getenv('API_URL')}/{numero_pedido}"
    response = requests.get(url, auth=(os.getenv("API_USER"), os.getenv("API_PASS")))

    if response.status_code == 200:
        dados = response.json()
        if isinstance(dados, list) and len(dados) > 0:
            pedido = dados[0]
            pedido_marketplace = pedido.get('pedido_marketplace', '')
            canal = pedido.get('canal', '')
            entregas = pedido.get('entregas', [])
            itens = entregas[0].get('itens', []) if entregas else []
            sku = itens[0].get('sku', '') if itens else ''
            notas_fiscais = entregas[0].get('notas_fiscais', []) if entregas else []
            if notas_fiscais and len(notas_fiscais) > 0:
                xml_content = notas_fiscais[0].get('xml', '')
                if xml_content:
                    abrir_tela_edicao(xml_content, pedido_marketplace, canal, sku)
                    return
    messagebox.showerror("Erro", "Erro ao carregar o pedido ou XML não encontrado.")

# Tela para o usuário informar o número do pedido
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
    root.geometry("600x400")

    Label(root, text="Informe o número do pedido:", font=("Arial", 14)).pack(pady=20)
    entry_pedido = Entry(root, width=40, font=("Arial", 12))
    entry_pedido.pack(padx=20, pady=10)

    Button(root, text="Carregar Pedido", bg="#2196F3", fg="white", font=("Arial", 12), command=ao_confirmar).pack(pady=20)

    root.mainloop()

# Tela para exibir dados e permitir edição
def abrir_tela_edicao(xml_content, pedido_marketplace, canal, sku):
    root_xml = ET.fromstring(xml_content)
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    nome_cliente = root_xml.find('.//nfe:dest/nfe:xNome', ns)
    cep_atual = root_xml.find('.//nfe:dest/nfe:enderDest/nfe:CEP', ns)
    xmun_atual = root_xml.find('.//nfe:dest/nfe:enderDest/nfe:xMun', ns)
    uf_atual = root_xml.find('.//nfe:dest/nfe:enderDest/nfe:UF', ns)

    nome_cliente = nome_cliente.text if nome_cliente is not None else ""
    cep_atual = cep_atual.text if cep_atual is not None else ""
    xmun_atual = xmun_atual.text if xmun_atual is not None else ""
    uf_atual = uf_atual.text if uf_atual is not None else ""

    root = Tk()
    root.title("Editor de XML")
    root.geometry("600x400")

    # Copia pedido marketplace para área de transferência
    root.clipboard_clear()
    root.clipboard_append(pedido_marketplace)

    status = StringVar()
    status.set("Pedido carregado com sucesso.")

    # Exibe informações do pedido
    Label(root, text=f"Nome do Cliente: {nome_cliente}", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(20, 5))
    Label(root, text=f"Pedido Marketplace: {pedido_marketplace}", font=("Arial", 12)).grid(row=1, column=0, columnspan=2)
    Label(root, text=f"Canal: {canal}", font=("Arial", 12)).grid(row=2, column=0, columnspan=2)
    Label(root, text=f"SKU: {sku}", font=("Arial", 12)).grid(row=3, column=0, columnspan=2)
    Label(root, text=f"CEP atual: {cep_atual}", font=("Arial", 12)).grid(row=4, column=0, columnspan=2)
    Label(root, text=f"Município atual: {xmun_atual}", font=("Arial", 12)).grid(row=5, column=0, columnspan=2)
    Label(root, text=f"UF atual: {uf_atual}", font=("Arial", 12)).grid(row=6, column=0, columnspan=2)

    var_cep = IntVar()
    var_xmun = IntVar()
    var_uf = IntVar()

    # Campos editáveis
    Checkbutton(root, text="Alterar CEP", variable=var_cep,
                command=lambda: entry_cep.config(state=NORMAL if var_cep.get() else DISABLED), font=("Arial", 12)).grid(row=7, column=0, sticky='w', padx=20, pady=5)
    entry_cep = Entry(root, width=40, state=DISABLED, font=("Arial", 12))
    entry_cep.grid(row=7, column=1, padx=20, pady=5)

    Checkbutton(root, text="Alterar Município", variable=var_xmun,
                command=lambda: entry_xmun.config(state=NORMAL if var_xmun.get() else DISABLED), font=("Arial", 12)).grid(row=8, column=0, sticky='w', padx=20, pady=5)
    entry_xmun = Entry(root, width=40, state=DISABLED, font=("Arial", 12))
    entry_xmun.grid(row=8, column=1, padx=20, pady=5)

    Checkbutton(root, text="Alterar UF", variable=var_uf,
                command=lambda: entry_uf.config(state=NORMAL if var_uf.get() else DISABLED), font=("Arial", 12)).grid(row=9, column=0, sticky='w', padx=20, pady=5)
    entry_uf = Entry(root, width=40, state=DISABLED, font=("Arial", 12))
    entry_uf.grid(row=9, column=1, padx=20, pady=5)

    # Botão para salvar
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

    Button(root, text="Salvar Documento Modificado", bg="#4CAF50", fg="white", font=("Arial", 12), command=ao_clicar).grid(row=10, column=0, columnspan=2, pady=30)
    Label(root, textvariable=status, fg="blue", font=("Arial", 12)).grid(row=11, column=0, columnspan=2, pady=10)

    root.mainloop()

# Verifica variáveis de ambiente
USUARIO = os.getenv("API_USER")
SENHA = os.getenv("API_PASS")
URL_BASE = os.getenv("API_URL")

if not USUARIO or not SENHA or not URL_BASE:
    raise ValueError("API_USER, API_PASS ou API_URL não estão definidos no ambiente.")

# Inicia o app
abrir_tela_pedido()
