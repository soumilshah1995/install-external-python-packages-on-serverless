try:
    import sys
    from awsglue.transforms import *
    from awsglue.utils import getResolvedOptions
    from pyspark.context import SparkContext
    from awsglue.context import GlueContext
    from awsglue.job import Job
except Exception as e:
    pass


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1660773467364 = glueContext.create_dynamic_frame.from_catalog(
    database="sampledb",
    table_name="mytable",
    transformation_ctx="AWSGlueDataCatalog_node1660773467364",
)

# Script generated for node Apply Mapping
ApplyMapping_node1660773505020 = ApplyMapping.apply(
    frame=AWSGlueDataCatalog_node1660773467364,
    mappings=[
        ("last_name", "string", "last_name", "string"),
        ("first_name", "string", "first_name", "string"),
        ("email", "string", "email", "string"),
    ],
    transformation_ctx="ApplyMapping_node1660773505020",
)

# Script generated for node Amazon S3
AmazonS3_node1660773507696 = glueContext.write_dynamic_frame.from_options(
    frame=ApplyMapping_node1660773505020,
    connection_type="s3",
    format="json",
    connection_options={"path": "s3://soumilshah-copy-1995", "partitionKeys": []},
    transformation_ctx="AmazonS3_node1660773507696",
)

job.commit()
