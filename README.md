# Editor de XML para Pedidos

Este projeto é um aplicativo Python com interface gráfica (Tkinter) para consultar pedidos na API da BC Ferramentaria, editar campos do XML da nota fiscal e gerar um arquivo no formato JSON salvo em `.txt`. O resultado é aberto automaticamente no Bloco de Notas.

## 🔑 Funcionalidades
- Consulta de pedido na API por número do pedido.
- Edição de campos do XML (CEP, xMun, UF) com seleção dinâmica.
- Geração de arquivo JSON com o XML modificado e informações do pedido.
- Abertura automática do arquivo no Bloco de Notas.

## 🚀 Como executar

1️⃣ **Configure as variáveis de ambiente no terminal:**
```bash
set API_USER=seu_usuario
set API_PASS=sua_senha
set API_URL=https://sua_url
