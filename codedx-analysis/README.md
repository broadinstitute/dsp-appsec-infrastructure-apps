# Automating CodeDx Uploads

This sets up a pipeline that will automatically upload reports to CodeDx. 
This is necessary because the cluster blocks connecting with CodeDx directly from 
outside the cluster. This deployment creates a GCS bucket, a Pub/Sub topic and subscriber,
and a GKE deployment to listen for Pub/Sub messages. It then creates a storage notification that will send
a message to the Pub/Sub topic when a new item is uploaded to the bucket.
The deployment receives the message, fetches the item (a vulnerability report),
and uploads it to the appropriate CodeDx project. The Storage bucket item must be tagged 
with the CodeDx project i.e. `x-goog-meta-project:${CODEDX-PROJECT}`.