Array.prototype.first = function (){
    return this[0]
}

function toggleWordPosHide(){
    var wordName = this.id.slice(0, 0-"-word_name".length);
    var wordPos = document.getElementById(wordName + "-pos-s");
    wordPos.classList.toggle("hiden");
}

function toggleIntroHide(){
    document.getElementById("intro").classList.toggle("hiden");
}

function toggleAllPosHide(){
    wasShowed = Array.from(document.getElementsByClassName("pos-s")).first().classList.toggle("hiden");
    Array.from(document.getElementsByClassName("pos-s")).forEach(function(block){
        block.classList.toggle("hiden", wasShowed );
    })
}

function sendWordsRequest(event){
    if (event.key != "Enter" && !event.pointerType && !event.touches){
        return false;
    }
    let wordsRequest = document.getElementById("words_request_text")
    axios({
        method: "GET",  
        url: SERVER_URLS.add_words.concat("", wordsRequest.value)
    }).then(function (response) {
        addWordBlocks(response.data)
    })
    wordsRequest.value = ""
}

function addWordBlocks(wordHTML){
    wordBlocks = document.getElementsByClassName("word_blocks")[0]
    newBlock = document.createElement("div")
    newBlock.innerHTML = wordHTML.trim()
    newBlock.childNodes.forEach(function(child){
        wordBlocks.appendChild(child)
    })
    setWordBlocksListeners()
}

function sendDeleteWordsRequest(){
    wordDeleted = this.id.slice(0, 0-"-delete_button".length)
    axios({
        method: "GET",
        url: SERVER_URLS.delete_words.concat("", wordDeleted)
    })
    document.getElementById(wordDeleted.concat("", "-word_block")).remove()
}

function sentDeleteAllRequest(){
    if(!confirm("Are you sure you about that?")){
        return false
    }
    axios({
        method: "GET",
        url: SERVER_URLS.delete_all_words
    })
    Array.from(document.getElementsByClassName("word_block")).forEach(function(wordBlock){
        wordBlock.remove()
    })
}

function setWordBlocksListeners(){
    Array.from(document.getElementsByClassName("delete_button")).forEach(function(button){
        button.addEventListener("click", sendDeleteWordsRequest)
    })
    Array.from(document.getElementsByClassName("word_def")).forEach(function(wordDef){
        wordDef.addEventListener("click", copyDef)
    })
    Array.from(document.getElementsByClassName("word_name")).forEach(function(wordDef){
        wordDef.addEventListener("click", toggleWordPosHide)
    })
    
}

function copyDef(){
    def = this.innerHTML
    navigator.clipboard.writeText(def)
}

function init(){
    document.getElementById("words_request").addEventListener("keyup", sendWordsRequest)
    setWordBlocksListeners()
    introButton = document.getElementById("intro_button")
    introButton.addEventListener("click", toggleIntroHide)
    deleteAllButton = document.getElementById("delete_all_button")
    deleteAllButton.addEventListener("click", sentDeleteAllRequest)
    sendWordsButton = document.getElementById("send_words_button")
    sendWordsButton.addEventListener("click", sendWordsRequest)
    showHideAllButton = document.getElementById("show_hide_all_button")
    showHideAllButton.addEventListener("click", toggleAllPosHide)
}