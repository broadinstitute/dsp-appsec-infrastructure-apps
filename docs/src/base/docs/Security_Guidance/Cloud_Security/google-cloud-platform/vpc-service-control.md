# VPC Service Control

* If you need your data(buckets or bigquery) contained to a very specific project, consider using [https://cloud.google.com/vpc-service-controls/](https://cloud.google.com/vpc-service-controls/)
  * This is mostly for very secure(PII) kind of data -- it ensures that data doesn’t leave the cloud. This would be for things like truly identifiable data, government controlled data or data that carries a certain contractual restriction.

