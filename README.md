# What is this

[Paperless-ng](https://github.com/jonaswinkler/paperless-ng) is a great document management system but lacks an important feature for me, which is automatic life cycle management for documents. This means that I can mark a document for auto-removal (or not, see below) after a certain amount of time passes since it is added to the system. 

This is a quick&dirty solution which does not need to modify the data model but instead uses the API and a cronjob to periodically check for documents that need to be removed. 

# How it works

paperless_lcm will check for tags on your documents that start with `LCM_prefix` and check if the document creation date + the amount of time specified in the tag is greated than the current date. If so, depending on the `AUTO_DELETE` flag it will either add a "to be removed" tag or **DELETE** your document if `AUTO_DELETE=yes`. 

**WARNING**: Be REALLY careful. This will DELETE your documents. The script is provided as is with no responsibility over your deployment. Test it first. 

LCM tags should be in the <LCM_PREFIX><value><units> like:
  * `LCM_15d` if you want the document to be removed in 15 days. 
  * `LCM_6m` if you want the document to be removed in 6 months. 
  * `LCM_1y` if you want the document to be removed in 1 year. 
  
 NOTE: Only days, months and years are supported. 

# How to install it

Create a config.ini file with the following contents:

```
[paperless]
HOST=<paperless URL>
USER=<user>
PASSWORD=<password>
AUTO_DELETE=<yes|no>
REMOVAL_TAG=<tag to apply>
LCM_PREFIX=<your tag prefix>
```
NOTE: `REMOVAL_TAG` has to exist. Won't be created.  
 
And then either deploy directly the script or use the provided [docker image](https://hub.docker.com/r/iverona/paperless_lcm). Then, setup a crontab rule to run it at the desired frequency. 
  
The script will look for config.ini either at the same folder or inside /config/ if running as a container. For example, run it as:

```
docker run --rm -v <Folder containing config.ini>:/config/ iverona/paperless_lcm
```
