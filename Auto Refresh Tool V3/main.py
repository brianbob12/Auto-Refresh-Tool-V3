import smtplib, ssl,time,datetime,subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def loadup():
    urls=[]
    urlLabels=[]
    temp=[]
    KWords=[]
    with open("watchList.txt","r") as f:
        temp=[i.split("::") for i in f.readlines()]
    with open("keywords.txt","r") as f:
        KWords=[i.lower().split(",")[:-1] for i in f.readlines()]
    for i in temp:
        urlLabels.append(i[0])
        urls.append(i[1])
    return urls,urlLabels,KWords

def sendEmail(index,newWords):
    print("sending email...")
    emailList=[]
    emailsFile="emails.txt"
    with open(emailsFile,"r")as f:
        emailList=[i for i in f.readlines()]
    print(emailList)
    changedWords=[]
    for i,v in enumerate(newWords):
        if v!=keyWordCount[index][i]:
            changedWords.append(keyWords[index][i])
            
    keyWordMessage="the keywords: "
    
    for i,word in enumerate(changedWords):
        if i==len(changedWords)-1:
            keyWordMessage+="'"+word+"'.\n"
        elif i==len(chnagedWords)-2:
            keyWordMEssage+="'"+word+"' and "
        else:
            keyWordMessage+="'"+word+"', "
    
    port = 465  # For SSL
    password = "testingPass"
    senderEmail="autoemailmachine@gmail.com"
    subject="Refresh Tool: "+labels[index]+" updated"

    text=""
    htmlPart="<html>\n<body>\n<p>\n"
    text+="The webpage:"+labels[index]+" was updated\n"
    htmlPart+="The webpage:<b>"+labels[index]+"</b> was updated<br>\n"
    text+=links[index]+" was updated\n"
    htmlPart+=keyWordMessage[:-2]+"<br>"
    text+=keyWordMessage
    htmlPart+='<a href="'+links[index]+'">'+links[index]+'</a><br>\n'
    text+="date and time: "+str(datetime.datetime.now())+" (US format)\n"
    htmlPart+="date and time: "+str(datetime.datetime.now())+" (US format)<br>\n"
    htmlPart+="</p>\n</body>\n</html>"


    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(senderEmail, password)
        for i in emailList:
            message=MIMEMultipart("alternative")
            message["Subject"]=subject
            message["From"]=senderEmail
            message["To"]=i
            part1=MIMEText(text,"plain")
            part2=MIMEText(htmlPart,"html")
            message.attach(part1)
            message.attach(part2)
            
            server.sendmail(senderEmail,i,message.as_string())
            
    print("email sent")

def getHTML():
    out=[]
    for i in links:
        if i=="dud":
            out.append("dud")
        else:
            res=subprocess.check_output(["curl",i[:-1]])
            out.append(res)
    return [i.lower() for i in out]

def countKeyWords(index,code):
    words=keyWords[index]
    new=[]
    for i in range(len(words)):
        new.append(code.count(words[i].encode()))
    return new


links,labels,keyWords=loadup()
HTML=getHTML()
keyWordCount=[countKeyWords(i,HTML[i]) for i in range(len(links))]
keyWordCount=[i for i in keyWordCount]

while True:
    new=getHTML()
    for index,value in enumerate(new):
        if value!=HTML[index]:
            print("\n\n"+labels[index],"updated")
            newWords=countKeyWords(index,value)
            if newWords!=keyWordCount[index]:
                print("key words changed")
                HTML[index]=value
                sendEmail(index,newWords)
                keyWordCount[index]=[i for i in newWords]
                time.sleep(30)
            else:
                print("keywords unchanged")
                print("\t",newWords,"\t",keyWordCount[index])
    time.sleep(1)
