pull_request
This event occurs when there is activity on a pull request. For more information, see "About pull requests." For information about the APIs to manage pull requests, see the GraphQL API documentation or "Pulls" in the REST API documentation.

For activity related to pull request reviews, pull request review comments, pull request comments, or pull request review threads, use the pull_request_review, pull_request_review_comment, issue_comment, or pull_request_review_thread events instead.

To subscribe to this event, a GitHub App must have at least read-level access for the "Pull requests" repository permission.

Availability for pull_request
Repositories
Organizations
GitHub Apps
Webhook payload object for pull_request
A pull request was assigned to a user.

Headers
Name, Type, Description
Body parameters
Name, Type, Description
action string Required
Value: assigned

assignee object or null Required
enterprise object
An enterprise on GitHub.

installation object
The GitHub App installation. This property is included when the event is configured for and sent to a GitHub App.

number integer Required
The pull request number.

organization object
A GitHub organization.

pull_request object Required
Properties of pull_request
repository object Required
A repository on GitHub.

sender object Required
A GitHub user.

