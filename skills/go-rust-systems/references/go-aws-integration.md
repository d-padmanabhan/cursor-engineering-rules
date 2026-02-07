# AWS & Cloud Integration

## AWS SDK for Go (v2)

**Client Configuration:**

```go
import (
    "context"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/service/s3"
    "github.com/aws/aws-sdk-go-v2/aws"
)

// Load default config (from env vars, credentials file, IAM role)
cfg, err := config.LoadDefaultConfig(context.TODO())
if err != nil {
    return fmt.Errorf("failed to load AWS config: %w", err)
}

// Create client
s3Client := s3.NewFromConfig(cfg)

// GOOD: Client factory with retry configuration
func NewS3Client(ctx context.Context, region string) (*s3.Client, error) {
    cfg, err := config.LoadDefaultConfig(ctx,
        config.WithRegion(region),
        config.WithRetryMaxAttempts(5),
    )
    if err != nil {
        return nil, fmt.Errorf("failed to load AWS config: %w", err)
    }
    return s3.NewFromConfig(cfg), nil
}
```

**Error Handling:**

```go
import (
    "github.com/aws/aws-sdk-go-v2/service/s3"
    "github.com/aws/aws-sdk-go-v2/service/s3/types"
    "github.com/aws/smithy-go"
)

func GetObject(ctx context.Context, client *s3.Client, bucket, key string) ([]byte, error) {
    result, err := client.GetObject(ctx, &s3.GetObjectInput{
        Bucket: aws.String(bucket),
        Key:    aws.String(key),
    })
    if err != nil {
        var nsk *types.NoSuchKey
        if errors.As(err, &nsk) {
            return nil, fmt.Errorf("object not found: %w", ErrNotFound)
        }

        var apiErr smithy.APIError
        if errors.As(err, &apiErr) {
            return nil, fmt.Errorf("AWS API error: %s - %s", apiErr.ErrorCode(), apiErr.ErrorMessage())
        }

        return nil, fmt.Errorf("failed to get object: %w", err)
    }
    defer result.Body.Close()

    return io.ReadAll(result.Body)
}
```

**Pagination:**

```go
import "github.com/aws/aws-sdk-go-v2/service/s3"

func ListObjects(ctx context.Context, client *s3.Client, bucket string) ([]string, error) {
    var keys []string
    paginator := s3.NewListObjectsV2Paginator(client, &s3.ListObjectsV2Input{
        Bucket: aws.String(bucket),
    })

    for paginator.HasMorePages() {
        page, err := paginator.NextPage(ctx)
        if err != nil {
            return nil, fmt.Errorf("failed to list objects: %w", err)
        }

        for _, obj := range page.Contents {
            keys = append(keys, aws.ToString(obj.Key))
        }
    }

    return keys, nil
}
```

**Lambda Handler Pattern:**

```go
import (
    "context"
    "github.com/aws/aws-lambda-go/lambda"
    "github.com/aws/aws-sdk-go-v2/service/dynamodb"
)

var dynamoClient *dynamodb.Client

func init() {
    cfg, _ := config.LoadDefaultConfig(context.TODO())
    dynamoClient = dynamodb.NewFromConfig(cfg)
}

type Event struct {
    UserID string `json:"user_id"`
}

type Response struct {
    StatusCode int    `json:"status_code"`
    Body       string `json:"body"`
}

func handler(ctx context.Context, event Event) (Response, error) {
    // Use global client
    result, err := dynamoClient.GetItem(ctx, &dynamodb.GetItemInput{
        TableName: aws.String("users"),
        Key: map[string]types.AttributeValue{
            "id": &types.AttributeValueMemberS{Value: event.UserID},
        },
    })
    if err != nil {
        return Response{StatusCode: 500, Body: "Internal error"}, err
    }

    return Response{StatusCode: 200, Body: "Success"}, nil
}

func main() {
    lambda.Start(handler)
}
```

**Context Propagation:**

```go
func ProcessWithTimeout(ctx context.Context, client *s3.Client, bucket, key string) error {
    // Create context with timeout
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    // Context automatically propagates cancellation
    _, err := client.GetObject(ctx, &s3.GetObjectInput{
        Bucket: aws.String(bucket),
        Key:    aws.String(key),
    })
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            return fmt.Errorf("operation timed out: %w", err)
        }
        return fmt.Errorf("failed to get object: %w", err)
    }

    return nil
}
```

**Region Validation:**

```go
var allowedRegions = map[string]bool{
    "us-east-1": true,
    "us-west-2": true,
    "eu-west-1": true,
}

func ValidateRegion(region string) error {
    if !allowedRegions[region] {
        return fmt.Errorf("invalid region: %s", region)
    }
    return nil
}
```
