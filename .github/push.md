push
This event occurs when a commit or tag is pushed.

To subscribe to this event, a GitHub App must have at least read-level access for the "Contents" repository permission.

Note: An event will not be created when more than three tags are pushed at once.

Availability for push
Repositories
Organizations
GitHub Apps
Webhook payload object for push
Headers
Name, Type, Description
Body parameters
Name, Type, Description
after string Required
The SHA of the most recent commit on ref after the push.

base_ref string or null Required
before string Required
The SHA of the most recent commit on ref before the push.

commits array of objects Required
An array of commit objects describing the pushed commits. (Pushed commits are all commits that are included in the compare between the before commit and the after commit.) The array includes a maximum of 20 commits. If necessary, you can use the Commits API to fetch additional commits. This limit is applied to timeline events only and isn't applied to webhook deliveries.

Properties of commits
compare string Required
URL that shows the changes in this ref update, from the before commit to the after commit. For a newly created ref that is directly based on the default branch, this is the comparison between the head of the default branch and the after commit. Otherwise, this shows all commits until the after commit.

created boolean Required
Whether this push created the ref.

deleted boolean Required
Whether this push deleted the ref.

enterprise object
An enterprise on GitHub.

forced boolean Required
Whether this push was a force push of the ref.

head_commit object or null Required
installation object
The GitHub App installation. This property is included when the event is configured for and sent to a GitHub App.

organization object
A GitHub organization.

pusher object Required
Metaproperties for Git author/committer information.

Properties of pusher
ref string Required
The full git ref that was pushed. Example: refs/heads/main or refs/tags/v3.14.1.

repository object Required
A git repository

sender object
A GitHub user.