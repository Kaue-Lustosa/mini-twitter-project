# Mini-Twitter

A scalable REST API for a Twitter-like social media platform, where users can register, create posts, follow other users, and view their feed.

## Features

- User registration and authentication using JWT
- Create, edit, delete, and like posts
- Retweet and reply to posts
- Follow and unfollow other users
- View feed of posts from followed users
- Hashtags and user mentions
- Trending hashtags
- Direct messaging between users
- Notifications for likes, follows, retweets, replies, and mentions
- Search functionality for posts, users, and hashtags
- Caching for improved performance
- Asynchronous task processing with Celery
- Comprehensive test coverage
- API documentation with Swagger

## Tech Stack

- Python 3.9
- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis (for caching and Celery)
- Celery (for asynchronous tasks)
- Docker & Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Installation

1. Clone the repository:
   \`\`\`
   git clone https://github.com/yourusername/mini-twitter.git
   cd mini-twitter
   \`\`\`

2. Start the application using Docker Compose:
   \`\`\`
   docker-compose up -d
   \`\`\`

3. Create a superuser (admin):
   \`\`\`
   docker-compose exec web python manage.py createsuperuser
   \`\`\`

4. The API will be available at http://localhost:8000/
5. API documentation is available at http://localhost:8000/swagger/

## API Endpoints

### Authentication

- `POST /api/users/token/`: Obtain JWT token
- `POST /api/users/token/refresh/`: Refresh JWT token

### Users

- `POST /api/users/`: Register a new user
- `GET /api/users/me/`: Get current user
- `GET /api/users/{id}/`: Get user by ID
- `POST /api/users/{id}/follow/`: Follow a user
- `POST /api/users/{id}/unfollow/`: Unfollow a user
- `GET /api/users/{id}/followers/`: Get user's followers
- `GET /api/users/{id}/following/`: Get users that a user is following

### Profiles

- `GET /api/users/profiles/`: List all profiles
- `GET /api/users/profiles/{id}/`: Get profile by ID
- `GET /api/users/profiles/my_profile/`: Get current user's profile
- `PUT /api/users/profiles/update_my_profile/`: Update current user's profile

### Posts

- `GET /api/posts/`: List all posts
- `POST /api/posts/`: Create a new post
- `GET /api/posts/{id}/`: Get post by ID
- `PUT /api/posts/{id}/`: Update a post
- `DELETE /api/posts/{id}/`: Delete a post
- `POST /api/posts/{id}/like/`: Like a post
- `POST /api/posts/{id}/unlike/`: Unlike a post
- `POST /api/posts/{id}/retweet/`: Retweet a post
- `POST /api/posts/{id}/unretweet/`: Unretweet a post
- `GET /api/posts/{id}/replies/`: Get replies to a post
- `GET /api/posts/feed/`: Get current user's feed
- `GET /api/posts/trending_hashtags/`: Get trending hashtags

### Notifications

- `GET /api/notifications/`: List all notifications for the current user
- `POST /api/notifications/{id}/mark_as_read/`: Mark a notification as read
- `POST /api/notifications/mark_all_as_read/`: Mark all notifications as read

### Messages

- `GET /api/messages/`: List all conversations for the current user
- `POST /api/messages/`: Create a new conversation
- `GET /api/messages/{id}/`: Get a conversation by ID
- `GET /api/messages/{id}/messages/`: Get messages in a conversation
- `POST /api/messages/{id}/send_message/`: Send a message in a conversation
- `GET /api/messages/unread_count/`: Get the count of unread messages

## Running Tests

\`\`\`
docker-compose exec web python manage.py test
\`\`\`

## Project Structure

\`\`\`
mini_twitter/
├── mini_twitter/          # Project settings
├── users/                 # User management app
├── posts/                 # Posts, likes, retweets app
├── notifications/         # Notifications app
├── messages/              # Direct messaging app
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker configuration
└── requirements.txt       # Python dependencies
\`\`\`

## Database Schema

The project uses the following database schema:

- **User**: Django's built-in User model
- **Profile**: Extended user profile with bio, avatar, and follower/following counts
- **Follow**: Represents a follow relationship between users
- **Post**: User posts with content, image, and counts for likes, retweets, and replies
- **Like**: Represents a like on a post
- **Retweet**: Represents a retweet of a post
- **Hashtag**: Represents a hashtag used in posts
- **PostHashtag**: Links posts to hashtags
- **Mention**: Represents a user mention in a post
- **Notification**: Represents notifications for various activities
- **Conversation**: Represents a conversation between users
- **Message**: Represents a message in a conversation

## Caching Strategy

The project uses Redis for caching:

- User feeds are cached for 5 minutes
- Cache is invalidated when a user follows/unfollows another user or likes/unlikes a post

## Asynchronous Tasks

Celery is used for handling asynchronous tasks:

- Sending email notifications when a user follows another user

## Security Features

- JWT authentication
- Rate limiting on API endpoints
- Input validation
- CSRF protection