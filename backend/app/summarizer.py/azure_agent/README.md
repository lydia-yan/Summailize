# Azure AI Setup

- [Azure AI Setup](#azure-ai-setup)
  - [Prerequisites](#prerequisites)
  - [Create Azure AI Language Resource](#create-azure-ai-language-resource)
    - [✅ After deployment](#-after-deployment)
  - [Create a OpenAI Deployment in Azure AI Studio](#create-a-openai-deployment-in-azure-ai-studio)
    - [✅ After created](#-after-created)
  - [Create Azure OpenAI Resource for Python SDK/API (Optional)](#create-azure-openai-resource-for-python-sdkapi-optional)
    - [After created](#after-created)

## Prerequisites
- Have a active Azure account: [Sign up](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account?icid=azurefreeaccount)
- Python 3.7+
- `pip install azure-ai-language-textanalytics azure-identity`

## Create Azure AI Language Resource
1. Go to the [Azure Portal](https://azure.microsoft.com/en-us/get-started/azure-portal)
2. Click **"Create a resource"** → Search for **“Language”**
3. Select **Language** → Click **Create**
4. Fill in:
   - Subscription
   - Resource group
   - Region (e.g., East US, West Europe that close to you)
   - Name (e.g., my-language-resource)
5. Select Pricing Tier (Free F0 or Standard S)

### ✅ After deployment
1. Go to **"Resource Overview"** of your created Language resource
2. In the left sidebar, click **“Keys and Endpoint”**
   - **Key**: Copy either **KEY 1** or **KEY 2**
   - **Endpoint**: Copy the **Endpoint URL**(usually starts with `https://<resource-name>.cognitiveservices.azure.com/`)

Use these values in your `.env` file:
```bash
    AZURE_LANGUAGE_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
    AZURE_LANGUAGE_KEY=<your-key>
```

## Create a OpenAI Deployment in Azure AI Studio
1. Go to [Azure AI Studio (Foundry)](https://ai.azure.com/)
2. Log in with your Microsoft/Azure account.
3. Find the **Azure OpenAI** and click **“Use a resource”**
4. You can either create a new resouce here or use the created Azure OpenAI resouce you created in Microsoft Azure  
   1. Create a new one
      1. Choose:
           - Your subscription (e.g., "Visual Studio Enterprise", "Pay-As-You-Go", etc.)
           - Your Azure resource created in Azure OpenAI (e.g., summarize-openai)
      2. Then click **“Use resource”**
   2. Used the Azure resource created in Azure OpenAI
      1. Select the resource
      2. Go to steps for **"After created"** in below

### ✅ After created 
1. In the left sidebar, click: **Shared resources** → **Deployments**
2. Click the blue **+ Deploy model** button to create a new deployment
3. Fill in: 
   - **Model**: `gpt-4o-mini` (most cost efficient or choose whatever model you want)
   - **Deployment name**: Give it a name like `gpt4o` or `email-summarizer`
   - Default values (optional): You can leave defaults or adjust `temperature`, etc. later
4. Click **"Create"** or **"Deploy"** at the bottom

Note:  It may take 1–2 minutes to deploy. Once it's ready:
- You will see the created model listed under the **Deployments** tab
- Go into **Deployments** tab or check the main page of resource, you will find out:
   - **Key**: Copy either **KEY 1** or **KEY 2**
   - **Endpoint**: Copy the **Endpoint URL**(usually starts with `https://<resource-name>.cognitiveservices.azure.com/`)
- You can now use the **deployment name**, **API key**, and **endpoint** in your Python code

Use these values in your `.env` file:
```bash
    AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview
    AZURE_OPENAI_API_KEY=<your-key>
```

## Create Azure OpenAI Resource for Python SDK/API (Optional)
1. Go to [Azure Portal](https://azure.microsoft.com/en-us/get-started/azure-portal)
2. Click **“Create a resource”** → Search for **"Azure OpenAI"**
3. Click **Create**
4. Fill in:
   - Subscription and Resource Group
   - Region: Must be a supported region (e.g., East US, South Central US, France Central)
   - Resource name: e.g., my-openai-api
5. Pricing tier: choose **Standard**
6. Review + Create → Click **Create**


### After created 
1. Go to your OpenAI resource 
2. (Optional) In the left sidebar, click **"Keys and Endpoint"** 
   - **Key**: Copy either **KEY 1** or **KEY 2**
   - **Endpoint**: Copy the **Endpoint URL**(usually starts with `https://<resource-name>.cognitiveservices.azure.com/`)

## Finish
Once you’ve filled in the `.env` file with:
- `AZURE_LANGUAGE_KEY` and `AZURE_LANGUAGE_ENDPOINT`
- `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`

**You’re all set! You can now run your Azure AI Language or Azure OpenAI in the Python application.**