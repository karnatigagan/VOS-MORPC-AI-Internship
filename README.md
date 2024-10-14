Gagan Karnati - Taking up the LLM task - 
# VOS-MORPC-AI-Internship
-> Village Of Somerset / Mid-Ohio Regional Planning Commission
Historical General Sheridan LLM for internship LLaMA With LangChain Integration

The General Sheridan Project is a complex AI and historical simulation tool designed to create interactive experiences with historical figures like General Philip Sheridan. The project focuses on running and fine-tuning large language models (LLMs) like LLaMA to generate text-based interactions that reflect the personality and historical knowledge of the character. 

historical simulation tool designed around AI-powered interaction, utilizing cutting-edge language models (LLaMA 3) fine-tuned to simulate complex historical characters. The project blends NLP, web development, ethical considerations, and historical research, with future aspirations of expanding to other communities and improving the technical foundation. The main challenges revolve around fine-tuning the models for a nuanced and accurate portrayal of historical figures and handling the computational demands of running large language models.

- Will be using M3 Max Macbook Pro to run this project. Utilizing M3 Max resources - Latest and Highest end Laptop from Apple...
- M3 Max GPU comparable to a low end latest RTX 4060 Nvidia GPU.
















Goal of readme - Document it well enough that you can at least get it running.

### Hardware

Ideally, you'd want to run llama3 in GPU memory. I have a 3050 8GB, but it's not sufficient. I believe 12GB is sufficient from some experimentation with T4s. 10GB might work, but it'd be tight. If you don't have a sufficient graphics card, Ollama will run on the CPU automatically. Multi-core performance is key here.

### Installation

You'll need to install the following:
 * Ollama: probably latest is best, but v0.2.0 or higher is likely sufficient
 * Python 3.11 or higher. 3.12 might cause some warnings but is always fine in my testing.
Then, you'll need to run `ollama pull llama3:8b` to get the model and `ollama pull nomic-embed-text:latest` to get the text embeddings for the RAG.
Finally, `pip install -r requirements.txt` should get you ready.

### Running

There's three components that need to be running:
 * Ollama: Ollama likes to run itself in the background, but you can start it from the start menu (Windows) or, if you want to peek under the hood a little more, through the command line with `ollama serve`.
 * web server: the `/web` directory should be put under a simple static web server. For testing, you can run `python -m http.server` in this directory. This is vulnerable to simple attacks, though, so in production, you'll want something like nginx or Apache serving this directory.
 * Sanic: a Sanic production-ready web server serves as the middleground between Ollama and the frontend, managing user history, system prompts, that sort of stuff. Run `sanic general.server:app -p 1831 --dev` in the root (`General`) directory.
After that, you should be able to view the application at `localhost:8000`!

### Notes

 * I called this project "General" both after General Sheridan, and because it eventually should be a turnkey solution for other communities to make their own characters, hence "general". Eh, it kinda works. I think anyone else has only ever called it "the General Sheridan project".
 * If you don't know why 1831 was chosen as the port number for the websocket, you should probably do more history research before working on this project.
 * There's an RDF file with full source information (or at least as full as I have): that's intended to be loaded into Zotero, form Zotero you can view and edit them, create bibliographies, whatever
 * There's a git repo set up in here with the critical files tracked. I've only been comitting occasionally, but at least always with (reasonably) stable code. There's no remote for the repo, so it's not on GitHub or anything.
   * It almost certainly doesn't matter, but I've signed the commits just in case. It's the same key I [use on my GitHub](https://github.com/Eiim/MinecraftSoundReconstructor/commit/abe86605b224cac2d267e77e794b7d4f9daa7c80). The ID is BD5C277B544A867D.
 * Of course, remove the `--dev` flag from Sanic if running in prod.
 * There's a Langchain API key setting in there, for use with Langsmith. I recommend checking this out for some dev testing at least, because it's very useful for debugging your model. You'll need your own API key. Put it in the environment variable manually, doing it programatically doesn't work for some reason (at least on Windows).
 * We've talked about using cloud hardware instead of local hardware for running the LLM. It's remarkably easy to do so with Langchain. You might notice a commented out line in `llm.py` loading the llm with Baseten instead of Ollama. Unfortunately you can't just swap out these lines, there's some more code changes that need to happen to make history work, but it's pretty close. However, the bigger issue is that Baesten instances take minutes to load, at which point you might as well just run locally. If you want to explore this path, here's some more thoughts on cloud GPU:
   * You almost certainly want to be using serverless GPUs rather than cloud GPU servers. See [here](https://fullstackdeeplearning.com/cloud-gpus/).
   * T4s are dirt-cheap compared to any other sufficient serverless GPU offering right now. Some other options might be faster, though.
   * Given those requirements, there's two real options out there: Baseten and Covalent. There's very little to distinguish the two that I know of,  but I only played with Baseten. Covalent _might_ offer faster start-up, and they also offer free credits, so it should be easy enough to test them out.
   * There's another option out there, Mystic AI, but they have steep low-volume pricing, supposedly due to long startup times. They say they're going to improve this in the near future, so maybe keep an eye on them.
   * If you're using Baseten, you'll probably want to figure out how to deploy custom models using Truss. I followed [this example](https://github.com/basetenlabs/truss-examples/tree/main/llama/llama-3_1-8b-instruct) and got it working. Make sure you sign the Llama 3/3.1 agreement on HF if you're using them. You should get approved within an hour or so.
   * You could probably already  figure it out, but you'll need a Baseten API key too.
 * I spent like a week of my life trying to figure out fine-tuning. 
   * I still kinda believe that fine-tuning is ultimately going to be helpful. You can't properly emulate style any other way (few-shot is just not good enough), so it can make the character a lot more unique and showcase their individuality.
   * There's a 'finetuned_llama3' folder with some of the remnants of my attempts. Not sure if it'll help, but I included it anyways.
   * [Unsloth](https://github.com/unslothai/unsloth/) seems to be the best way to do fine-tuning, but it's still poorly documented (they claim to be improving this!).
   * I don't even know what to tell you about fine-tuning, honestly. "Fine-tune on completions only" is not what you want. Using a custom token as the prompt might work. Somehow this was easy with GPT-2 (I did it back when were were still using Python 2, remember that?) but is not with newer models.
 * Consider using Llama 3.1. I haven't really tested it out, but it should be an easy, though small, performance bump.
 * Consider using the "instruct" models, which are designed for Q&A, although arguably not this kind of Q&A.
 * Let's talk about sources:
   * Data that you put in the RAG should be public-domain, or at least under a very permissive license.
   * It's currently set up just to process raw text files, but can easily handle PDFs, Word docs, etc. See `unstructured`.
   * [Project Gutenberg](https://www.gutenberg.org/) is the best source for public-domain books. Sheridan's memoirs are in there, but nothing else from or about him.
   * After that, your best bet is to go trawling the [Internet Archive](https://archive.org/search?query=philip+henry+sheridan) for books, which includes a lot of OCR'd public-domain books. Be careful though, it also includes a lot of OCR'd books that are in copyright.
   * Google Books also has a lot of OCR'd books, but beware of the "license" on them. I'm not sure how legally binding it is, but it's somewhat restrictive and our use-case may not satisfy its requrements. Google Books scans can also pop up on the Internet Archive.
   * With OCR'd books, you'll want to clean them up before just dropping them in. At a minimum, trim off title page and any ending material. I find it helpful to split books into chapters (mostly for sourcing purposes later when I'm debugging), and also to remove page numbers/headers and combine paragraphs that were split up by page breaks. It's a lot of work but just doing the basics goes a long ways to making the text understandable for the model.
   * Also check on old newspapers. These are particularly great for collecting random anecdotes. Newspapers.com is the best source out there. I have access with a Worthington Public Libraries card, other libraries may or may not have access. But you should get library cards anyways, becauses libraries are good! (I have 4-6, depending on how you count them). Newpapers.com has OCR, which allows you to search for names and such easily, but it's not that great, so you may want to manually transcribe any articles you want to use.
   * Using sources from the community is a big plus. We've been looking into getting old letters Sheridan wrote from West Point. Hopefully you have those by now!
 * Little Phil is long dead. I don't personally have any real ethical qualms about simulating him with AI, so long as proper disclaimers are presented and the AI is rigourous enough. (note: I do not currently have the confidence that the AI is rigourous enough! Community testing and input in a closed-beta process should be valuable here.)
 * Philip is obviously a controversial figure, for good reasons. Most notably, his role in the Indian Wars is troubling. At a minimum, you should seek Native perspectives on the man. It might even make sense to ask tribes  for feedback on the project.
 * Other things we want to do in the maybe-near future:
   * Add basic feedback options. I've made a very rudimentary version of this for now, but eventually it will need to be more robust and easier to navigate.
   * Add the ability to see the sources that the RAG pulled for each message. This is started, the data is sent to the user, but it's not displayed yet.
   * Improve parallel conversations.
   * Stream tokens rather than sending entire messages at once. This would probably remove the need for the "..." messages. Not sure how to do this at the moment. I tried to get it working, but it streamed paragraphs rather than tokens. A bit odd.
  * Other things we want to do in the probably-farther future:
    * Make a back-end UI for admins to upload documents, tweak settings, etc
	* Talk to other communities about them adapting it for their figures
