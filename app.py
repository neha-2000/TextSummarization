from summarizer import Summarizer
from pprint import pprint
from flask import Flask, render_template, request
import sys
from bs4 import BeautifulSoup
import requests
import re
import heapq
import  nltk #used for summerization for traning (nltk
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from IPython.display import YouTubeVideo

app = Flask(__name__)
@app.route('/')
def main():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("index.html")

# below method extract content from web
def get_wiki_Content(url):
    req_obj=requests.get(url)
    text=req_obj.text
    soup=BeautifulSoup(text) #instantiate beautiful soup constructor
    all_paras=soup.find_all("p")
    wiki_text=''
    for para in all_paras:
        wiki_text+=para.text
    return wiki_text


@app.route("/bert", methods=['GET', 'POST'])
def bert():
    if request.method == "POST":
        # url = request.form.get("url")
        url=request.form['url']
        lines=request.form['line']
        url_content=get_wiki_Content(url)
        data = url_content.replace("\n",'')
        data = data.replace("\ufeff", "")
        print(url)
        print(data[0:100])
        model = Summarizer()
        result = model(data, num_sentences=5, min_length=60)
        url_content = ''.join(result)
        # pprint(full)
        #return url_content
        return render_template("summary.html" , output=url_content)
    else:
        return render_template("bert.html")

    
#Code for NLP   http://127.0.0.1:5000/static/news.html
@app.route("/nlp", methods=['GET', 'POST'])
def nlp():
    return render_template("nlp.html")
    

def nlp_summarize(data):
    news_text=data
    #  Data Preprocessing
    # news_text=get_wiki_Content(url)
    # print("URL",news_text)
    news_text=news_text.lower()

    # remove spaces, punctuations and numbers
    clean_text=re.sub('[^a-zA-Z]', ' ', news_text)
    clean_text= re.sub('\s+', ' ', clean_text)

    #nltk.download('stopwords')
    # print(clean_text)
    # split into sentence list
    sentence_list = nltk.sent_tokenize(news_text)
    
    #print(sentence_list)

    stopwords = nltk.corpus.stopwords.words('english')
    #Word Frequencies
    word_frequencies = {}
    for word in nltk.word_tokenize(clean_text):
        if word not in stopwords:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    maximum_frequency = max(word_frequencies.values())

    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / maximum_frequency

    #Calculate Sentence Scores
    sentence_scores = {}

    for sentence in sentence_list:
        for word in nltk.word_tokenize(sentence):
            if word in word_frequencies and len(sentence.split(' ')) < 30:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_frequencies[word]
                else:
                    sentence_scores[sentence] += word_frequencies[word]
    print(word_frequencies)
    print("-----------------------------",sentence_scores)
    summary = heapq.nlargest(10, sentence_scores, key=sentence_scores.get)
       
    summerize_text=" ".join(summary)
    
    return summerize_text

@app.route("/news", methods=['GET', 'POST'])
def news():
    url1='https://www.bbc.com/news/world-asia-58729701'
    # url1='https://www.nydailynews.com/'
    url2='https://en.wikipedia.org/wiki/Python_(programming_language)'
    if request.method == "POST":
        if request.form.get("submit_a"):
            print("button1")
            text=get_wiki_Content(url1)
            summerize_text=nlp_summarize(text)
            return render_template("summary.html" , output=summerize_text)


        elif request.form.get("submit_b"):
            print("button2")
            text=get_wiki_Content(url2)
            summerize_text=nlp_summarize(text)
            return render_template("summary.html" , output=summerize_text)
        elif  request.form.get("submit_c"):
            print("button 3")
            filename=request.form['file']
            print(filename)
            
            with open(filename,encoding="utf8") as file:
                print('File found')
                text=file.read()
                summerize_text=nlp_summarize(text)

                return render_template("summary.html" , output=summerize_text)
           
            #     data=file.read().replace('\n','')
            # data = data.replace("\ufeff", "")
            # summerize_text=nlp_summarize(data)
            # return render_template("summary.html" , output=summerize_text)

            

	    
    return render_template("news.html")


@app.route("/notes", methods=['GET', 'POST'])
def notes():
    if request.method == "POST":
        data=request.form.get('note')
        print(data)
        summerize_text=nlp_summarize(data)
        return render_template("summary.html" , output=summerize_text)


    return render_template("notes.html") 

def youtube_summary(url):
    youtube_video = url 
    video_id = youtube_video.split("=")[1]
    print(video_id)
    YouTubeVideo(video_id)
    YouTubeTranscriptApi.get_transcript(video_id)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(transcript[0:5])

    result = ""
    for i in transcript:
        result += ' ' + i['text']
        #print(result)
    print(len(result))

    summarizer = pipeline('summarization')

    num_iters = int(len(result)/1000)
    summarized_text = []
    for i in range(0, num_iters + 1):
        start = 0
        start = i * 1000
        end = (i + 1) * 1000
        out = summarizer(result[start:end])
        out = out[0]
        out = out['summary_text']
        summarized_text.append(out)
    print(summarized_text)

    print(len(summarized_text))
    return summarized_text



@app.route("/video", methods=['GET', 'POST'])
def video():
    if request.method == "POST":
        url = request.form.get("url")
        # url=request.form['url']
        summarized_text=youtube_summary(url)
        print(type(summarized_text))
        return render_template("summary.html" , output=summarized_text)
    return render_template("video.html")


if __name__ == "__main__":
    app.run(debug=True)