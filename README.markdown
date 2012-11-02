Nudge is a Django app that lets you selectively push content from one Django server (we'll call this "staging") to another ("production").

When staging code, you might find it necessary to preview that code with real data. You might also use your staging-side Django admin as your primary content creation environment, in order to beef up security on your production end.

If you do either of these, moving content from staging to production requires copying your entire database from one server to another. Nudge fixes this. Nudge will let you move new and modified content from staging to production. As content is created, deleted, and modified in staging, Nudge will keep track of it. When you are ready to move that content to production, create a batch. Add whatever content necessary to that batch; ignore the content that is not yet ready to be sent to production. Save the batch and deploy it. The content in the batch will be immediately available in your production environment.

Nudge was inspired by the RAMP plugin for WordPress and wouldn't be possible without the incredible django-reversion version control extension.

You should understand how Reversion works before proceeding with nudge, and any models you'll want to use with Nudge should be enabled for Reversion.

https://github.com/etianen/django-reversion

## Installation

1. Install nudge with 'pip install django-nudge'
2. add 'nudge' to your INSTALLED_APPS
3. add nudge to your URL configuration, on your both servers: like: url(r'^nudge-api/', include('nudge.urls')),
4. run manage.py syncdb

## Using Nudge

1. Use your favorite method of enabling django-reversion for your models.
2. generate a key by running ./manage.py new_nudge_key. Set this to NUDGE_KEY in both settings.py (staging and production)
3. in the staging settings.py, set NUDGE_REMOTE_ADDRESS to the 'nudge-api'  URL of your production server 'http://somehost/nudge-api/'
4. in the staging settings.py, set NUDGE_SELECTIVE to a list any models that you want to use with Nudge (and are already being managed by reversion), like ['jobmanager.job', 'knowledgebase.question']