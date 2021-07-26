import boto3
import json
import os
import argparse

def create_website(bucket_name, website_folder):

	# Write the S3 bucket policy to make the contents accessable
	bucket_policy = {
	 'Version': '2012-10-17',
	 'Statement': [{
		 'Sid': 'AddPerm',
		 'Effect': 'Allow',
		 'Principal': '*',
		 'Action': ['s3:GetObject'],
		 'Resource': "arn:aws:s3:::%s/*" % bucket_name
	  }]
	}

	bucket_policy = json.dumps(bucket_policy)
	
	
	s3 = boto3.client('s3')

	s3.create_bucket(Bucket=bucket_name)
	
	s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
	
	# GIve permission to the bucket to host static website
	s3.put_bucket_website(
	 Bucket=bucket_name,
	 WebsiteConfiguration={
	 'ErrorDocument': {'Key': 'error.html'},
	 'IndexDocument': {'Suffix': 'index.html'}
	}
	)
	
	# Ship website files to S3
	for file in os.listdir(website_folder):
		f = open(website_folder + '/' + file, 'rb')
		data = f.read()
		s3.put_object(  Body=data,
						Bucket=bucket_name,
						Key=file,
						ContentType='text/html' )
		f.close()
	return 'http://{}.s3-website-{}.amazonaws.com/'.format(bucket_name, region_name)


def main():

	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--name',required = True, type=str, help='bucket_name')
	parser.add_argument('--folder',required = True,type=str, help='website_folder' )
	args = parser.parse_args()
	create_website(args.name, args.folder)

if __name__ == '__main__':
	main()