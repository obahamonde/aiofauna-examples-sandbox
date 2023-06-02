repository
This event occurs when there is activity relating to repositories. For more information, see "About repositories." For information about the APIs to manage repositories, see the GraphQL documentation or "Repositories" in the REST API documentation.

To subscribe to this event, a GitHub App must have at least read-level access for the "Metadata" repository permission.

Availability for repository
Enterprises
Repositories
Organizations
GitHub Apps
Webhook payload object for repository
A repository was archived.

Headers
Name, Type, Description
Body parameters
Name, Type, Description
action string Required
Value: archived

enterprise object
An enterprise on GitHub.

installation object
The GitHub App installation. This property is included when the event is configured for and sent to a GitHub App.

organization object
A GitHub organization.

repository object Required
A repository on GitHub.

sender object Required
A GitHub user.

