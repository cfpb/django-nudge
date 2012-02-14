Nudge is a Django app that lets you selectively move data from a staging environment to your production environment.

When staging code, you might find it necessary to preview that code with real data. You might also use your staging-side Django admin as your primary content creation environment, in order to beef up security on your production end.

If you do either of these, moving content from staging to production requires copying your entire database from one server to another. Nudge fixes this. Nudge will let you move new and modified content from staging to production. As content is created, deleted, and modified in staging, Nudge will keep track of it. When you are ready to move that content to production, create a batch. Add whatever content necessary to that batch; ignore the content that is not yet ready to be sent to production. Save the batch and deploy it. The content in the batch will be immediately available in your production environment.

Nudge was inspired by the RAMP plugin for WordPress and wouldn't be possible without the incredible django-reversion version control extension.