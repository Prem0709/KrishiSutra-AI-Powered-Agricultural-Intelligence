# 🚀 Quick Deployment Guide for HuggingFace Spaces

## ✅ What's Already Done

Your project is **ready to deploy**! Here's what has been completed:

1. ✓ Created Gradio app (`app.py`) compatible with HuggingFace Spaces
2. ✓ Updated `README.md` with HF Spaces metadata
3. ✓ Fixed `requirements.txt` with all dependencies
4. ✓ Committed and pushed all changes to GitHub
5. ✓ Added HuggingFace remote repository

---

## 📝 Deploy to HuggingFace Spaces (3 Simple Steps)

### Step 1: Get Your HuggingFace Token

1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"** or use an existing one with **write** access
3. Copy the token (starts with `hf_...`)

### Step 2: Configure the Deployment Script

Edit `deploy_to_hf.ps1` and replace `<YOUR_HF_TOKEN>` with your actual token:

```powershell
$HF_TOKEN = "hf_your_actual_token_here"
```

### Step 3: Run the Deployment Script

Open PowerShell in your project directory and run:

```powershell
cd "f:\Bharat Fellowship\samarth"
.\deploy_to_hf.ps1
```

**That's it!** Your Space will be live at:
https://huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence

---

## 🔐 Secure Your API Keys (Recommended)

After deployment, add your API keys as **Secrets** in HuggingFace:

1. Go to: https://huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence/settings
2. Scroll to **"Repository secrets"**
3. Click **"New secret"** and add:

   | Name | Value |
   |------|-------|
   | `GOOGLE_API_KEY` | `AIzaSyCdSM2oDPOOe3YfcmFPQY6R3dccjY7Ah2c` |
   | `DATA_GOV_API_KEY` | `579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b` |

4. Your `app.py` already supports reading these from environment variables!

---

## 🧪 Test Locally Before Deploying

Run this to test your Gradio app:

```powershell
python app.py
```

Then visit: http://localhost:7860

---

## 🐛 Troubleshooting

### If deployment fails:

1. **Check build logs** in your HuggingFace Space
2. **Verify data files** exist in `data/` folder
3. **Check API keys** are configured correctly

### Manual Push (Alternative Method):

```powershell
# Remove existing remote
git remote remove huggingface

# Add remote with token in URL
git remote add huggingface https://Premkumar0709:<YOUR_TOKEN>@huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence

# Push
git push huggingface main --force
```

---

## 📊 After Deployment

### Your Space will be available at:
https://huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence

### It may take 2-5 minutes to build and start.

### You can:
- Share the link with others
- Embed it in your website
- Monitor usage in the Space analytics
- Enable discussions for user feedback

---

## 💡 Next Steps

1. **Customize your Space**:
   - Add a thumbnail image
   - Update description and tags
   - Enable community features

2. **Monitor performance**:
   - Check build logs
   - View usage statistics
   - Respond to user feedback

3. **Keep it updated**:
   ```powershell
   git add .
   git commit -m "Update description"
   git push huggingface main
   ```

---

## 📚 Useful Links

- **Your Space**: https://huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence
- **GitHub Repo**: https://github.com/Prem0709/KrishiSutra-AI-Powered-Agricultural-Intelligence
- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **Gradio Docs**: https://www.gradio.app/docs

---

## 🎉 Good Luck!

Your AI-powered agricultural intelligence platform is ready to help farmers and policymakers make data-driven decisions!

---

*Developed by Premkumar Pawar | Multi-Agent RAG with Gemini*
