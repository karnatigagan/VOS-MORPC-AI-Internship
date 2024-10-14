import getpass
import os
import signal
import time
import uuid
from threading import Event, Thread
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Baseten

sources_dict = {
    "./data\\asheridanstory.txt": "\"A Sheridan Story\", Chicago Times, December 17th 1888",
    "./data\\heroshenandoah_c1.txt": "The life of Gen. P. H. Sheridan, the hero of the Shenandoah, Chapter 1",
    "./data\\letter-coe.txt": "Letter from L. W. Coe, dated April 6th 1856",
    "./data\\nyt 1861-06-08.txt": "\"The Great Insurrection; Special Dispatch from Washington\", New York Times, June 8th 1861",
    "./data\\oregonian 1888-08-06.txt": "\"Sheridan\", The Oregonian, August 6th 1888",
    "./data\\roe_1868.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1868",
    "./data\\roe_1869.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1869",
    "./data\\roe_1870.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1870",
    "./data\\roe_1871.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1871",
    "./data\\roe_1872.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1872",
    "./data\\roe_1873.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1873",
    "./data\\roe_1874.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1874",
    "./data\\roe_1875.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1875",
    "./data\\roe_1876.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1876",
    "./data\\roe_1877.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1877",
    "./data\\roe_1878.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1878",
    "./data\\roe_1879.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1879",
    "./data\\roe_1880.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1880",
    "./data\\roe_1881.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1881",
    "./data\\roe_1882.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, 1882",
    "./data\\roe_conclusion.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, Conclusion",
    "./data\\roe_intro.txt": "Record of Engagements with Hostile Indians within the Military Division of the Missouri, Introduction",
    "./data\\somersetpress 1874-03-27.txt": "Untitled column, Somerset Press, March 27th 1874",
    "./data\\somersetpress 1875-01-08.txt": "\"General Sheridan Proposes a Remedy\", Somerset Press, January 8th 1875",
    "./data\\somersetpress 1875-01-29.txt": "\"Sheridan in New Orleans\", Somerset Press, January 29th 1875",
    "./data\\timeline.txt": "Timeline of General Sheridan's life, Somerset Builder's Club",
    "./data\\wikipedia.txt": "Philip Sheridan, Wikipedia, July 3rd 2024",
    "./data\\yellowstone_report_9_20_1881.txt": "Expedition Through the Big Horn Mountains, Yellowstone Park, etc.",
    "./data\\v1c1.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 1",
    "./data\\v1c2.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 2",
    "./data\\v1c3.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 3",
    "./data\\v1c4.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 4",
    "./data\\v1c5.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 5",
    "./data\\v1c6.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 6",
    "./data\\v1c7.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 7",
    "./data\\v1c8.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 8",
    "./data\\v1c9.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 9",
    "./data\\v1c10.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 10",
    "./data\\v1c11.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 11",
    "./data\\v1c12.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 12",
    "./data\\v1c13.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 13",
    "./data\\v1c14.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 14",
    "./data\\v1c15.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 15",
    "./data\\v1c16.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 16",
    "./data\\v1c17.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 17",
    "./data\\v1c18.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 18",
    "./data\\v1c19.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 19",
    "./data\\v1c20.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 20",
    "./data\\v1c21.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 21",
    "./data\\v1c22.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 22",
    "./data\\v1c23.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 23",
    "./data\\v1c24.txt": "Personal Memoires of P. H. Sheridan, Volume 1, Chapter 24",
    "./data\\v2c1.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 1",
    "./data\\v2c2.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 2",
    "./data\\v2c3.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 3",
    "./data\\v2c4.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 4",
    "./data\\v2c5.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 5",
    "./data\\v2c6.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 6",
    "./data\\v2c7.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 7",
    "./data\\v2c8.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 8",
    "./data\\v2c9.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 9",
    "./data\\v2c10.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 10",
    "./data\\v2c11.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 11",
    "./data\\v2c12.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 12",
    "./data\\v2c13.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 13",
    "./data\\v2c14.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 14",
    "./data\\v2c15.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 15",
    "./data\\v2c16.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 16",
    "./data\\v2c17.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 17",
    "./data\\v2c18.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 18",
    "./data\\v2c19.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 19",
    "./data\\v2c20.txt": "Personal Memoires of P. H. Sheridan, Volume 2, Chapter 20"
}

class GeneralLLM():
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def __cleanup(self, interval, lifetime): # Both values in seconds
        stopped = Event()
        def loop():
            while not stopped.wait(interval):
                now = time.time()
                for id in list(self.sessions):
                    if now - self.sessions[id] >= lifetime:
                        del self.sessions[id]
                        if id in self.store:
                            del self.store[id]
                print(str(len(self.sessions))+" active sessions")
        Thread(target=loop).start()    
        return stopped.set
    
    def __shutdown(self, *args):
        print("Shutting down cleanly (ish)")
        if self.cleanup_stopper:
            self.cleanup_stopper()
    
    def __init__(self):
        self.store = {}
        self.sessions = {}
        
        signal.signal(signal.SIGINT, self.__shutdown)
        
        #if not os.environ.get("OPENAI_API_KEY"):
        #    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key: ")
        
        # Probably only temporary as we start building out the app
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        if not os.getenv("LANGCHAIN_API_KEY"):
            os.environ["LANGCHAIN_API_KEY"] = getpass.getpass("Langchain API Key: ")
        
        llm = ChatOllama(model="llama3:8b")
        # llm = Baseten(model="owprme83", deployment="development")
        print("LLM Loaded")
        
        # Load a directory into document objects
        docs = []
        for filename in os.listdir("./data"):
            loader = UnstructuredFileLoader(os.path.join("./data", filename))
            docs.append(loader.load()[0])
        
        print("Docs loaded")
        
        # Split and embed documents to create a retriever
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OllamaEmbeddings(model="nomic-embed-text"))
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 5})
        print("Docs embedded")
        
        # 2. Incorporate the retriever into a question-answering chain.
        system_prompt = (
            "You are an AI playing the role of General Philip Sheridan. "
        	"You will answer any questions about your life factually. "
        	"You will answer in the style of General Sheridan. "
            "If asked where you're from, you will say that you grew up in Somerset, Ohio. "
        	"If something is unclear, you will admit you are an AI and state that your knowledge and capabilities are limited. "
            "ONLY the follow information for history about your life. If a historical detail is not in the following, do not say it. However, do not mention this information specifically."
            "\n\n"
            "{context}"
        )
        
        # Generic contextualization step
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )
        
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        self.conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        
        self.cleanup_stopper = self.__cleanup(300, 43200)
    
    def init_chat(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = time.time()
        print(self.sessions)
        return session_id
    
    async def invoke(self, question, session_id):
        self.sessions[session_id] = time.time()
        resp = self.conversational_rag_chain.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}},
        )
        sources = set()
        for source in resp["context"]:
            sources.add(sources_dict[source.metadata["source"]])
        print(sources)
        return (resp["answer"], sources)
