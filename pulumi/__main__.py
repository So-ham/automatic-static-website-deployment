"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3, cloudfront, acm


# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket('my-bucket',
    website=s3.BucketWebsiteArgs(
       index_document='index.html'
    ))

# Upload index.html and make it public
bucketObject = s3.BucketObject(
    'index.html',
    acl='public-read',
    content_type='text/html',
    bucket=bucket,
    source=pulumi.FileAsset('index.html'),
)

# Creating a Cloudfront Distribution
cdn = cloudfront.Distribution('cdn',
	enabled=True,
	default_root_object='index.html',
	origins=[cloudfront.DistributionOriginArgs(
        origin_id=bucket.arn,
        domain_name=bucket.website_endpoint,
        custom_origin_config=cloudfront.DistributionOriginCustomOriginConfigArgs(
            origin_protocol_policy='http-only',
            http_port=80,
            https_port=443,
            origin_ssl_protocols=['TLSv1.2'],
        )
    )],
	default_cache_behavior=cloudfront.DistributionDefaultCacheBehaviorArgs(
        target_origin_id=bucket.arn,
        viewer_protocol_policy='redirect-to-https',
        allowed_methods=['GET', 'HEAD', 'OPTIONS'],
        cached_methods=['GET', 'HEAD', 'OPTIONS'],
        forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(forward='none'),
            query_string=False,
        ),
        min_ttl=0,
        default_ttl=60 * 10,
        max_ttl=60 * 10,
    ),
    restrictions=cloudfront.DistributionRestrictionsArgs(
        geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type='none'
        )
       ),
     viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
        acm_certificate_arn=acm.Certificate("cert",
		    domain_name=bucket.website_endpoint,
		    tags={
		        "Environment": "test",
		    },
		    validation_method="DNS"),
        ssl_support_method='sni-only'
    )
   )
# Export the s3 bucket_name and cloudfront domain name
pulumi.export('bucket_endpoint', pulumi.Output.concat('http://', bucket.website_endpoint))
pulumi.export('cloudfront_domain', cdn.domain_name)