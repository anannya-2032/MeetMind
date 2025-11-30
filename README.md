# MeetMind
A Multi-Agent AI System that Fetches Meet Transcripts, Generates MoM, Extracts Action Items, Saves to Drive, Sends Email Updates &amp; Creates Calendar Tasks.

**📌 Overview**  
MeetMind is an intelligent, fully automated Minutes-of-Meeting (MoM) generator built using the Google Agent Development Kit (ADK) and powered by Gemini 2.0 models.  

It uses a multi-agent architecture to:  

✔ Fetch Google Meet transcripts automatically  
✔ Clean & format raw transcript text  
✔ Generate a professional MoM  
✔ Extract action items with deadlines & assignees  
✔ Save MoM to Google Drive  
✔ Email attendees the final MoM  
✔ Add tasks/reminders to Google Calendar  

MeetMind transforms online meeting chaos into structured, actionable information — autonomously.  

**🚀 Why This Project?**  
Meetings produce valuable information but capturing, formatting, storing, and distributing it is slow and error-prone when done manually. Traditional automation scripts cannot interpret long transcripts, extract tasks intelligently, or handle multi-step reasoning.  

MeetMind solves this by using agentic AI:  

✔ Multi-agent collaboration  
✔ LLM reasoning for complex text  
✔ Tool calling for Gmail, Drive, Calendar  
✔ Long-running operations  
✔ Context-aware workflow  
✔ Memory-enabled continuity  
This is more than automation — it’s intelligent orchestration.  

**⚙️ Features** :-  

📝 Automatic MoM Generation  
✔ Summarizes long, messy transcripts  
✔ Extracts decisions, discussions, and outcomes  

▶️ Action Item Extraction  
✔ Detects tasks  
✔ Assigns responsible people  
✔ Infers deadlines  
✔ Adds tasks to Google Calendar  

📂 Drive Storage  
✔ Saves MoM as a Google Doc  
✔ Keeps version history  
✔ Organizes by meeting name & date  

📧 Email Distribution  
✔ Identifies meeting attendees  
✔ Sends MoM via Gmail  
✔ Includes summary, files, and action items  

🤖 Multi-Agent Architecture  
✔ Orchestrator agent  
✔ Transcript fetch agent  
✔ Transcript cleanup agent  
✔ MoM generation agent  
✔ Action item extraction agent  
✔ Drive storage agent  
✔ Gmail dispatch agent  
✔ Calendar task agent  

🧠 Memory  
✔ Session memory for workflow  
✔ Long-term memory for recurring patterns  

**🏗️ Architecture**  
User  
  ↓   
Orchestrator Agent  
  ↓  
Transcript Fetch Agent  → Google Drive API  
  ↓  
Transcript Cleanup Agent  
  ↓  
MoM Generation Agent (LLM)  
  ↓  
Action Item Extraction Agent  
  ↓  
Drive Storage Agent  → Save MoM to Drive  
  ↓  
Email Dispatch Agent  → Send via Gmail  
  ↓  
Calendar Action Agent  → Create Tasks  
  ↓  
Final MoM Delivered  


Agents communicate using an in-memory session state and shared context objects.  

**📚 Technologies Used**  
🧠 AI & Agents  
✔ Google Agent Development Kit (ADK)  
✔ Gemini 2.0 Flash / Pro models  
✔ Sequential & parallel multi-agent pipelines  
✔ LoopAgents for quality control  
✔ Context Compaction & MemoryBank  

🔧 Tools & APIs  
✔ Google Drive API  
✔ Gmail API  
✔ Google Calendar API  
✔ Custom Python tools for:  
    Transcript parsing  
    Document generation  
    Email formatting  
    Action extraction  

**🧪 How It Works (Workflow Demo)**  
✔ User inputs meeting name or date  
✔ TranscriptFetchAgent locates Meet transcripts in Drive  
✔ CleanupAgent removes noise, timestamps & fillers  
✔ MoMAgent generates:  
    Summary  
    Agenda points  
    Decisions  
    Discussions  
✔ ActionItemAgent extracts tasks  
✔ DriveAgent stores final MoM  
✔ EmailAgent sends MoM to attendees  
✔ CalendarAgent creates task reminders  

