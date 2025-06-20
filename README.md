# 📝 Editor de XML para Pedidos

Este projeto é um aplicativo Python com interface gráfica (**Tkinter**) para consulta de pedidos via API, exibição e alteração de dados do XML da nota fiscal e geração de arquivo JSON para registro.  

O resultado é salvo em `.txt` e aberto automaticamente no Bloco de Notas para conferência.

---

## ⚙️ Funcionalidades

- 🔍 **Consulta de pedidos na API** por número do pedido.
- 🖥️ **Interface gráfica intuitiva** para edição dos dados do pedido.
- 📌 **Exibição dos dados atuais** no topo da tela:
  - Nome do cliente
  - CEP atual
  - Município atual (xMun)
  - UF atual
- ✏️ **Seleção dinâmica** dos campos que deseja alterar:
  - CEP
  - Município (xMun)
  - UF
- 💾 **Geração automática de arquivo JSON** contendo:
  - Número do pedido
  - Chave da nota fiscal
  - XML modificado com as alterações aplicadas
- 📝 **Abertura automática do arquivo** no Bloco de Notas.

---

## 🚀 Como executar

1️⃣ Configure as variáveis de ambiente no terminal (Windows):
```bash
set API_USER=seu_usuario
set API_PASS=sua_senha
set API_URL=https://sua_url/
