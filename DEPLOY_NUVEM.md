# 🌐 Como Colocar o Estudo Bíblico Online 24h na Nuvem
*(Acessível do seu celular, tablet ou qualquer lugar sem precisar do computador ligado)*

Este guia mostra como colocar sua **Jornada Bíblica 365** no ar gratuitamente, permitindo que você estude no celular, registre suas anotações e tenha acesso em tempo real mesmo com seu computador desligado.

---

## 📱 Opção 1: Render.com (Mais Recomendada • Gratuita)

O **Render** é uma das melhores plataformas gratuitas de hospedagem em nuvem para aplicações Python.

### Passo a Passo:

1. **Crie uma conta gratuita no GitHub** (se ainda não tiver):
   - Acesse [github.com](https://github.com) e crie sua conta gratuita.
   - Crie um repositório chamado `jornada-biblica-365` (pode ser público ou privado).
   - Envie os arquivos desta pasta para o repositório no GitHub (basta clicar em *Add file* ➔ *Upload files* e arrastar todos os arquivos).

2. **Crie uma conta no Render**:
   - Acesse [render.com](https://render.com) e entre com sua conta do GitHub.

3. **Criar o Serviço Web**:
   - No painel do Render, clique em **New +** ➔ **Web Service**.
   - Conecte o repositório `jornada-biblica-365` que você criou.
   - Configure os campos (já detectados automaticamente pelo nosso arquivo `render.yaml`):
     - **Name**: `jornada-biblica` (ou o nome que preferir)
     - **Environment**: `Python`
     - **Build Command**: `python generate_plan.py`
     - **Start Command**: `python server.py`
     - **Plan**: `Free` ($0/mês)
   - Clique em **Create Web Service**.

4. **Pronto! 🎉**:
   - Em cerca de 2 minutos, o Render fornecerá um link público seguro com HTTPS, por exemplo:
     👉 `https://jornada-biblica.onrender.com`
   - Você pode acessar esse link do seu celular, tablet ou trabalho a qualquer hora!

---

## 📲 Opção 2: PythonAnywhere (Upload Direto sem GitHub • Gratuito)

Se você preferir não usar o GitHub e quiser apenas enviar os arquivos direto pelo navegador:

1. Acesse [pythonanywhere.com](https://www.pythonanywhere.com/) e crie uma conta gratuita.
2. Na aba **Files**, crie uma pasta `jornada_biblica` e faça upload dos arquivos do projeto.
3. Na aba **Consoles**, abra um console Bash e execute:
   ```bash
   python generate_plan.py
   python server.py
   ```
4. Você terá seu site funcionando 24h em `https://seunome.pythonanywhere.com`.

---

## 📱 Como Instalar como Aplicativo no Celular (PWA)

Assim que você abrir o link da nuvem no seu celular (Google Chrome no Android ou Safari no iPhone):

### No Android:
1. Abra o link no Chrome do celular.
2. Toque nos **três pontinhos (⋮)** no topo direito.
3. Toque em **"Instalar aplicativo"** ou **"Adicionar à tela inicial"**.
4. O ícone de bíblia **📖 Jornada Bíblica** aparecerá na tela do seu celular como um app nativo!

### No iPhone (iOS):
1. Abra o link no Safari do iPhone.
2. Toque no botão de **Compartilhar** (quadrado com seta para cima).
3. Role para baixo e toque em **"Adicionar à Tela de Início"**.
4. Toque em **Adicionar**. O app abrirá em tela cheia sem barras de navegador!

---

## 💬 Como Ficam os Lembretes do WhatsApp com o PC Desligado?

Existem duas formas ideais de usar com o PC desligado:

1. **Botão 1-Clique Direto no Celular (Prático e Imediato)**:
   - Ao abrir o app no seu celular, no cartão do estudo de hoje há o botão **"Compartilhar Estudo no WhatsApp"**.
   - Ao tocar nele, o WhatsApp do seu celular abre imediatamente com a mensagem formatada para você enviar para si mesmo ou para seu grupo devocional.

2. **Lembrete 100% Automático na Nuvem**:
   - Para envio totalmente automático mesmo com o celular no bolso e PC desligado:
     - **Via Bot no Telegram (100% gratuito e oficial)**: O Telegram permite bots oficiais que enviam mensagens programadas sem precisar de QR Code nem de manter navegador aberto. Se você quiser, podemos adicionar o envio via bot do Telegram em 5 minutos!
     - **Via API de WhatsApp na Nuvem**: Serviços como Evolution API, Z-API ou Twilio rodam 24h na nuvem para WhatsApp comercial.
