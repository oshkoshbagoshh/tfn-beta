# TFN CTV Project

## File Upload Functionality

This project now supports file uploads for various media types:

### Supported Upload Types

- **Artist Images**: Upload images for artists
- **Album Cover Images**: Upload cover images for albums
- **Track Audio Files**: Upload audio files for tracks
- **Ad Campaign Videos**: Upload videos for ad campaigns

### Where Uploads Go

All uploaded files are stored in the `media/` directory at the project root, organized in subdirectories:

- Artist images: `media/artists/`
- Album cover images: `media/albums/`
- Track audio files: `media/tracks/`
- Ad campaign videos: `media/ads/`

Files are automatically renamed using UUID to prevent filename conflicts.

### Amazon S3 (production media)

When `AWS_STORAGE_BUCKET_NAME` is set, uploads go to that S3 bucket under the `media/` prefix instead of local `media/`. Set in `.env` or the environment:

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_STORAGE_BUCKET_NAME` | Yes (to enable S3) | S3 bucket name |
| `AWS_S3_REGION_NAME` | No | Region (default: `us-east-1`) |
| `AWS_S3_CUSTOM_DOMAIN` | No | Custom domain for URLs (e.g. CloudFront) |
| `AWS_DEFAULT_ACL` | No | Object ACL (default: `public-read`) |

Credentials: set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, or use an IAM role when running on AWS. See [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html).

### Testing File Uploads

To test file uploads:

1. Navigate to the appropriate form (e.g., ad campaign upload form)
2. Select a file to upload
3. Submit the form
4. The file will be uploaded to the appropriate directory

### Placeholder Images

The project uses placeholder SVG graphics from the static directory when no images are available.

If you want to use the Pexels API for placeholder images:

1. Get a Pexels API key from [Pexels API](https://www.pexels.com/api/)
2. Add your API key to the `.env` file:

   ```
   PEXELS_API_KEY=your_pexels_api_key_here
   ```
3. If you don't have python-dotenv installed, you can install it with:

   ```
   pip install python-dotenv
   ```

   Then uncomment the dotenv loading code in `tfn_ctv/settings.py`

### Dependencies

- Django 5.2.1
- For image processing (optional): Pillow
  ```
  pip install Pillow
  ```
- For fake data generation:
  ```
  pip install Faker requests
  ```

## Faker Factory

The project includes a faker factory to load the database with sample data. This is useful for development and testing purposes.

### Usage

To generate fake data, run the following command:

```bash
python manage.py generate_fake_data
```

This will create:

- 10 genres
- 20 artists with images from Unsplash
- 30 albums with cover images from Unsplash
- 100 tracks
- 15 users
- 10 ad campaigns with video placeholders from Unsplash
- 5 service requests

You can customize the number of entities to create by using the following options:

```bash
python manage.py generate_fake_data --genres 5 --artists 10 --albums 15 --tracks 50 --users 8 --ad_campaigns 5 --service_requests 3
```

## Email Configuration

All form submissions are sent to the development email specified in settings.py. By default, this is set to `developer@tfnms.co`.

The email backend is set to console backend for development, so emails will be printed to the console instead of being sent.

To change the development email, update the `DEVELOPER_EMAIL` setting in `tfn_ctv/settings.py`.
