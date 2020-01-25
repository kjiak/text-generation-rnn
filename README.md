# text-generation-rnn

# Credits
https://www.tensorflow.org/tutorials/sequences/text_generation <br />
<br />
Saving model: <br />
https://www.tensorflow.org/tutorials/keras/save_and_restore_models <br />
<br />
Serving: <br />
https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html <br />
https://towardsdatascience.com/deploying-keras-deep-learning-models-with-flask-5da4181436a2 <br />
https://2.python-requests.org/en/master/user/quickstart/ <br />

### git delete history 
git checkout --orphan temp_branch <br />
git add -A <br />
git commit -am "the first commit" <br />
git branch -D master <br />
git branch -m master <br />
git push -f origin master <br />

git reset --soft HEAD will achieve the same as it does not reset the index or the working directory <br/>
git reset --hard HEAD will rest the index and working directory (save a local copy) <br/>
