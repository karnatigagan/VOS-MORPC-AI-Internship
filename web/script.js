// Specify the WebSocket server URL
const socketUrl = 'ws://localhost:1831/chat';

var ws;
var session_id;

function setupWS() {
	// Create a new WebSocket object
	ws = new WebSocket(socketUrl);

	// Store session ID
	session_id = ""

	// WebSocket connection event listeners
	ws.onopen = () => {
		console.log('Connected to the WebSocket server.');
		ws.send("{\"type\": \"init\"}");
	};

	ws.onmessage = (event) => {
		result = JSON.parse(event.data)
		console.log(result)
		if(result.session_id !== undefined) {
			session_id = result.session_id
		}
		if(result.message !== undefined) {
			const chatHistory = document.getElementById('chat-history');
			
			for(l of chatHistory.getElementsByClassName('loading-container')) {
    			l.remove();
			}
			
			// Create a new message element
			const messageElement = document.createElement('div');
			messageElement.className = 'message-bot';
			messageElement.textContent = result.message;
			
			const voteElement = document.createElement('vote');
			const upvote = document.createElement('div');
			upvote.textContent = "👍";
			const downvote = document.createElement('div');
			downvote.textContent = "👎";
			voteElement.appendChild(upvote);
			voteElement.appendChild(downvote);
			messageElement.appendChild(voteElement);
			
			upvote.onclick = (e) => {sendVote(ws, voteElement, true)};
			downvote.onclick = (e) => {sendVote(ws, voteElement, false)};

			// Append the message to the chat history
			chatHistory.appendChild(messageElement);

			// Scroll to the bottom of the chat history
			chatHistory.scrollTop = chatHistory.scrollHeight;
		}
		if(result.loading === true && document.getElementsByClassName("loading").length == 0) {
    		const chatHistory = document.getElementById('chat-history');
    		const messageElement = document.createElement('div');
			messageElement.className = 'message-bot loading-container';
			const loadElement = document.createElement('loader');
			loadElement.textContent = '⬤ ⬤ ⬤';
			messageElement.appendChild(loadElement);
			chatHistory.appendChild(messageElement);
			chatHistory.scrollTop = chatHistory.scrollHeight;
		}
	};

	/*ws.onerror = (error) => {
		console.log('WebSocket error:', error);
		let reconnect = window.confirm("Something went wrong with the AI connection. Press OK to attempt to reconnect.");
		if(reconnect) {
			resetChat();
		}
	};*/

	ws.onclose = () => {
		console.log('Disconnected from the WebSocket server.');
		let reconnect = window.confirm("Disconnected from the AI. Press OK to attempt to reconnect.");
		if(reconnect) {
			resetChat();
		}
	};
}

function sendVote(ws, element, positive) {
    ctx = ""
	// Is this the most rigourous way to get the text? Definitely not. But it's good enough for beta testing.
    for(n of element.parentNode.parentNode.childNodes) {
        if(n.nodeName != "#text") {
            ctx += n.childNodes[0].textContent + "\n"
			if(n === element.parentNode) {
                break;
            }
        }
    }
    ws.send(JSON.stringify({type: "vote", context: ctx, vote: positive, session_id: session_id}));
    
    const thankElement = document.createElement('thanks');
    element.appendChild(thankElement);
    setTimeout(() => thankElement.remove(), 2000);
}

function sendMessage() {
	const input = document.getElementById('chat-input');
	const message = input.value.trim();

	if (message === '') return;

	const chatHistory = document.getElementById('chat-history');

	// Create a new message element
	const messageElement = document.createElement('div');
	messageElement.className = 'message-human';
	messageElement.textContent = message;

	// Append the message to the chat history
	chatHistory.appendChild(messageElement);

	// Clear the input
	input.value = '';

	// Scroll to the bottom of the chat history
	chatHistory.scrollTop = chatHistory.scrollHeight;
	
	// Send message
	ws.send(JSON.stringify({type: "message", message: message, session_id: session_id}));
}

function handleKeyPress(event) {
	if (event.key === 'Enter') {
		sendMessage();
	}
}

function resetChat() {
	const chatHistory = document.getElementById('chat-history');
	chatHistory.replaceChildren();
	chatHistory.scrollTop = 0;
	ws.close();
	setupWS();
}

setupWS();