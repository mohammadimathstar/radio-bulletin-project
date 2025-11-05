# 📻 Radio Bulletin Knowledge Graph Project

## 🧠 Overview

This project focuses on the **automatic construction of a Knowledge Graph (KG)** from historical **Dutch radio bulletin scripts** archived at the **Dutch National Library (Koninklijke Bibliotheek)**.  
The goal is to enable **researchers, historians, and journalists** to efficiently explore complex networks of **people, organizations, events, and locations** described in these historical broadcasts.

The radio bulletins—broadcasts that informed the Dutch public during the interwar and early WWII period—represent a **rich historical dataset** reflecting political tensions, media framing, and public communication patterns of the era.

By transforming these unstructured textual archives into a **structured, searchable knowledge graph**, this project bridges **cultural heritage** and **modern AI-driven information extraction**.

---

## 🗂️ Dataset Description and Importance

The dataset consists of **radio bulletin scripts** digitized and archived by the **Dutch National Library (KB.nl)**. These bulletins provide an invaluable primary source for understanding:

- The **media narrative** leading up to and during World War II  
- The **language and framing** used to report global events to the Dutch audience  
- The **relationships** between political figures, nations, and institutions as perceived through contemporary reporting  

For this proof of concept, we focus specifically on the **year 1939**, which includes approximately **2,000 bulletins** — a pivotal year preceding the outbreak of WWII.  
This limited but meaningful subset provides an ideal testing ground for scalable NLP and knowledge graph construction techniques.

---

## 🎯 Objectives

1. **Data Ingestion & Preparation**  
   Retrieve and clean historical bulletin text from the KB archive.  
   
2. **Entity and Relation Extraction**  
   Use large language models (LLMs) to identify and link entities such as people, locations, and organizations, and detect relationships among them (e.g., “Hitler → delivers speech → Berlin”).  

3. **Knowledge Graph Construction**  
   Represent the extracted knowledge as an interconnected graph suitable for semantic querying and exploration.

4. **Thematic Exploration**  
   Employ **topic modeling** to narrow the focus to specific thematic areas of interest.

---

## 🧭 Focus of the Proof of Concept

As a first implementation, this project concentrates on **1939 bulletins** (~2,000 scripts) and narrows the scope to **three main topics**, identified through **BERT2Vec-based topic modeling**.  

Thematic clusters and representative keywords include:

### 1. Political and International Relations  
`['hitler', 'den', 'volk', 'polen', 'oorlog', 'landen', 'roosevelt', 'staten', 'rede', 'rijk', 'mussolini', 'president', 'vrede', 'europa', 'minister', 'engeland', 'dantzig']`

### 2. Diplomatic Activity and Press Coverage
`['berlijn', 'minister', 'ambassadeur', 'londen', 'hitler', 'besprekingen', 'ontvangen', 'president', 'polen', 'hoofdstad', 'engeland', 'pers', 'ministers', 'onderhoud', 'dantzig']`


### 3. Sports and Weather Reports  
`['sec', 'min', 'meter', 'gewonnen', 'klasse', 'wedstrijd', 'record', 'honkbal', 'afstand', 'kilometer', 'winnaar', 'overwinning', 'regen', 'bewolkt']`


This thematic filtering produced around **200 bulletins** for detailed processing and entity–relation extraction.  
Entity and relation extraction was performed using **DeepSeek**, an LLM-based model optimized for structured information extraction.

More details on the data processing workflow and KG construction are available in the [project documentation](https://github.com/mohammadimathstar/radio-bulletin-project/edit/master/packages/knowledge_engineering/docs/project_overview.md).

---

## 🕸️ Why Knowledge Graphs Matter

A **Knowledge Graph (KG)** organizes extracted entities and their relations into a **network of meaning** rather than isolated records.  
For researchers and journalists, this enables:

- **Exploratory querying** — e.g., “Which countries were most frequently mentioned with Hitler in 1939 broadcasts?”  
- **Temporal analysis** — tracking changes in discourse or entity relationships over time  
- **Event reconstruction** — linking speeches, political actions, and reactions across multiple sources  
- **Hypothesis generation** — discovering unexpected co-occurrences or missing links in media narratives  

In short, the KG transforms historical text archives into **searchable, explorable knowledge networks** — allowing domain experts to move from keyword search to **semantic understanding**.

---

## ⚙️ Challenges and Research Directions

### 1. Scale and Automation
Constructing a knowledge graph for the entire corpus of radio bulletins requires **millions of entity and relation detections**, which is computationally and logistically intensive.

### 2. Annotation Bottleneck
To train or fine-tune models for entity/relation recognition, **annotated data** is required — which is costly to create manually for historical texts.

### 3. Using LLMs to Create Silver Datasets
To overcome the lack of human annotations, LLMs can be used to automatically generate **“silver-standard” datasets** (semi-automated annotations).  
However, ensuring their quality is a key challenge.

Two promising strategies explored in this project are:

- **Multi-Model Comparison** — use several LLMs and cross-compare their outputs to identify consistent predictions.  
- **Self-Critique and Refinement** — prompt an LLM to **review and critique its own output**, improving the reliability of entity and relation extraction.

These approaches balance **scalability** and **accuracy**, providing a foundation for more robust KG creation in larger datasets.

---

## 🧰 Tools and Methods

| Component | Technology |
|------------|-------------|
| Data Ingestion | Custom scraper using KB API |
| Topic Modeling | BERT2Vec embeddings + clustering |
| Entity/Relation Extraction | DeepSeek LLM |
| KG Construction | Networkx |
| Storage & Visualization | Neo4j graph database |


---

## 📎 Reference

For detailed process documentation, data schema, and KG construction methodology, see:  
👉 [Project Overview Document](https://github.com/mohammadimathstar/radio-bulletin-project/edit/master/packages/knowledge_engineering/docs/project_overview.md)


