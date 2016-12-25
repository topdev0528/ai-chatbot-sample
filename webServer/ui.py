import os
import ast
from bson.objectid import ObjectId

from flask import request
from webServer import app

from core.models import Story,LabeledSentences,Parameter,update_document
from core.intentClassifier import IntentClassifier

import buildResponse

@app.route('/insertLabeledSentence', methods=['POST'])
def insertLabeledSentence():
    story = Story.objects.get(id=ObjectId(request.form['storyId']))
    labeledSentence = LabeledSentences()
    print(ast.literal_eval(request.form['labeledSentence']))
    labeledSentence.data = ast.literal_eval(request.form['labeledSentence'])
    story.labeledSentences.append(labeledSentence)
    try:
        story.save()
    except Exception as e:
        return {"error": e}
    return buildResponse.sentOk()


@app.route('/createStory', methods=['POST'])
def createStory():
    content = request.get_json(silent=True)

    story = Story()
    story.storyName = content.get("storyName")
    story.intentName = content.get("intentName")
    story.speechResponse = content.get("speechResponse")

    if content.get("parameters"):
        for param in content.get("parameters"):
            parameter = Parameter()
            update_document(parameter,param)
            story.parameters.append(parameter)
    try:
        story.save()
    except Exception as e:
        return {"error": e}
    return buildResponse.sentOk()

@app.route('/saveEditStory', methods=['POST'])
def saveEditStory():
    story = Story.objects.get(id=ObjectId(request.form['_id']))
    data = {
        "labels": request.form['labels'].split(","),
        "actionType": request.form['actionType'],
        "actionName": request.form['actionName'],
        "storyName": request.form['storyName'],
    }
    try:
        story.update(**data)
    except Exception as e:
        return {"error": e}
    return buildResponse.sentOk()


@app.route('/getStories', methods=['POST'])
def getStories():
    stories = Story.objects
    return buildResponse.sentJson(stories.to_json())


@app.route('/deleteStory', methods=['POST'])
def deleteStory():
    Story.objects.get(id=ObjectId(request.form['storyId'])).delete()

    try:
        intentClassifier = IntentClassifier()
        intentClassifier.train()
    except:
        pass

    try:
        os.remove("models/%s.model" % request.form['storyId'])
    except OSError:
        pass
    return buildResponse.sentOk()


@app.route('/deleteLabeledSentences', methods=['POST'])
def deleteLabeledSentences():
    story = Story.objects.get(id=ObjectId(request.form['storyId']))
    story.labeledSentences.filter(id=ObjectId(request.form['sentenceId'])).delete()
    story.save()
    return buildResponse.sentOk()