---
title: KrishiSutra AI Powered Agricultural Intelligence
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🌾 Project Samarth — AI Q&A Assistant (Gemini Powered)

### Empowering Smart Agriculture using Multi-Agent RAG and Google Gemini

---

## 🚀 Overview

**Project Samarth** is an intelligent, end-to-end **AI Q&A assistant** that enables policymakers, researchers, and farmers to query and analyze government agricultural and climate datasets directly through natural language.

It leverages  **Google Gemini** ,  **HuggingFace embeddings** , and a **Multi-Agent Retrieval-Augmented Generation (RAG)** system to extract, reason, and synthesize insights across diverse datasets hosted on  **[data.gov.in](https://data.gov.in)** .

---

## 🎯 Vision

Government portals like *data.gov.in* host thousands of valuable public datasets from ministries such as the **Ministry of Agriculture & Farmers Welfare** and the  **India Meteorological Department (IMD)** .

However, these datasets exist in  **inconsistent formats and structures** , making it difficult to derive actionable, cross-domain insights.

**Project Samarth** bridges this gap through a unified conversational interface that connects climate, agricultural, and policy data to enable evidence-based decision-making.

---

## 🧠 System Architecture

<pre class="overflow-visible!" data-start="1198" data-end="1472"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>User Query
   ↓
Auto Agent Detection (Climate / Agriculture / Scheme / KCC)
   ↓
Relevant Dataset Loader
   ↓
Context Retrieval (RAG Layer using HuggingFace embeddings)
   ↓
Google Gemini (models/gemini-pro-latest)
   ↓
Response Generation with Data-backed Reasoning
</span></span></code></div></div></pre>

### 🔹 Multi-Agent RAG Architecture

| Agent                         | Role                                                         | Data Source                                              |
| ----------------------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| 🌦️**Climate Agent**   | Handles temperature, rainfall, and IMD datasets              | `Mean_Temp_IMD_2017.csv`,`Sub_Division_IMD_2017.csv` |
| 🌾**Agriculture Agent** | Manages crop yield, mandi price, and production data         | `Current Daily Price of Commodities.csv`               |
| 🧾**Scheme Agent**      | Provides information from PM-KISAN and subsidy datasets      | `GetPMKisanDatagov.json`                               |
| ☎️**KCC Agent**       | Fetches live Kisan Call Center data using `data.gov.in`API | Live API Integration                                     |

---

## 💬 Example Questions

* “Compare the average annual rainfall in Tamil Nadu and Kerala for the last 10 years.”
* “Identify the district in Maharashtra with the highest rice yield in 2020.”
* “Analyze the trend of sugarcane production in Uttar Pradesh over the last decade.”
* “List government schemes supporting drought-resistant crops in Rajasthan.”
* “Correlate rainfall and crop yield in Punjab during 2015–2020.”

---

## 🧩 Key Features

✅ **Multi-Agent Intelligence** — Domain-specific reasoning for climate, agriculture, and policy data.

✅ **Gemini-Powered Responses** — Uses `models/gemini-pro-latest` for factual and concise answers.

✅ **Data Traceability** — Each answer is backed by the corresponding dataset.

✅ **Plug-and-Play Data Upload** — Upload your own CSV, Excel, or JSON datasets.

✅ **Auto Agent Detection** — Automatically identifies whether a query relates to climate, crop, or scheme data.

✅ **Streamlit Frontend** — Elegant and responsive UI for quick Q&A.

---

## 🛠️ Tech Stack

| Layer                   | Technology                               |
| ----------------------- | ---------------------------------------- |
| **Frontend**      | Streamlit                                |
| **LLM Backend**   | Google Gemini API                        |
| **Embeddings**    | HuggingFace                              |
| **RAG Framework** | Custom multi-agent retriever             |
| **Data Source**   | data.gov.in (IMD, Agriculture, PM-KISAN) |
| **Language**      | Python 3.10+                             |

---

## 📂 Project Structure

<pre class="overflow-visible!" data-start="3407" data-end="3835"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>SAMARTH/
│
├── agents/
│   ├── climate_agent.py
│   ├── agriculture_agent.py
│   ├── scheme_agent.py
│   └── kcc_agent.py
│
├── data/
│   ├── Mean_Temp_IMD_2017.csv
│   ├── Sub_Division_IMD_2017.csv
│   ├── </span><span>Current</span><span> Daily Price </span><span>of</span><span> Various Commodities.csv
│   └── GetPMKisanDatagov.json
│
├── utils/
│   ├── api_fetcher.py
│   ├── data_loader.py
│   └── rag_helper.py
│
├── config.yaml
├── main_app.py
└── requirements.txt
</span></span></code></div></div></pre>

---

## ⚙️ Setup Instructions

1. **Clone Repository**

   <pre class="overflow-visible!" data-start="3895" data-end="3995"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>git </span><span>clone</span><span> https://github.com/<your-repo>/project-samarth.git
   </span><span>cd</span><span> project-samarth
   </span></span></code></div></div></pre>
2. **Create Virtual Environment**

   <pre class="overflow-visible!" data-start="4034" data-end="4139"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python -m venv samarth_env
   </span><span>source</span><span> samarth_env/bin/activate  </span><span># or activate on Windows</span><span>
   </span></span></code></div></div></pre>
3. **Install Dependencies**

   <pre class="overflow-visible!" data-start="4172" data-end="4221"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>pip install -r requirements.txt
   </span></span></code></div></div></pre>
4. **Set Environment Variables**

   * Add your **Google Gemini API key** and **data.gov.in API key** in `config.yaml`
5. **Run Application**

   <pre class="overflow-visible!" data-start="4368" data-end="4411"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>streamlit run main_app.py
   </span></span></code></div></div></pre>
6. **Access**

   Open `http://localhost:8502` in your browser.

---

## 📸 Demo Screenshot

---

## 🧾 Sample Response

> **Query:** “Compare the average temperature of Tamil Nadu and Kerala in 2010”
>
> **Response:** “Based on the available IMD data, Tamil Nadu recorded an average temperature of ~28.7°C while Kerala averaged ~26.9°C. Source: Mean_Temp_IMD_2017.csv”

---

## 🎥 Submission Details

* **Loom Demo Video:** [Insert Public Loom Link Here]
* **Live Prototype (optional):** [Insert Streamlit Share / Hugging Face Space Link]

---

## 🏆 Evaluation Criteria Alignment

| Criterion               | How It’s Addressed                                          |
| ----------------------- | ------------------------------------------------------------ |
| Problem Solving         | Handles cross-domain query synthesis (climate + agriculture) |
| System Architecture     | Modular multi-agent RAG design                               |
| Accuracy & Traceability | Dataset-backed responses                                     |
| Data Sovereignty        | Works offline / local deployment supported                   |
| Creativity              | Combines Gemini reasoning with Indian public datasets        |

---

## 👨‍💻 Developer

**Premkumar Pawar**

🔗 [LinkedIn](https://www.linkedin.com/in/) | 💻 [GitHub](https://github.com/)

*Building data-driven AI solutions for a smarter agriculture ecosystem.*
