# Smart-Sub-deploy-Guide
如已完成本方案原型的部署，请参考 [使用说明](SmartSub-usage-CHN.md) 。

## 资源总体说明
本方案原型共需部署以下资源：

序号 | 资源类型 | 资源名称 
----|------|------
1 | SNS Topic | NotifyMe
2 | S3 Bucket | \<YOUR\_BUCKET\_NAME>
3 | IAM Role | ssRole 
4 | Lambda Function | ss-01-start-job
5 | Lambda Function | ss-02-status-check
6 | Lambda Function | ss-03-save-reko-result
7 | Lambda Function | ss-04-sub-creation
8 | Step Functions | smart-sub

## 环境准备
部署说明中的命令参考 [AWS CLI Version 2 命令规范](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html#cli-aws)，需要根据 [官方文档](https://docs.aws.amazon.com/zh_cn/cli/latest/userguide/install-cliv2.html) 提前安装好 AWS CLI version 2 工具，并配置好拥有 Admin Account 中 **管理员权限** 的 AKSK。如您已经安装 AWS CLI Version 1，可对应本方案原型参考 [AWS CLI Version 1 命令规范](https://docs.aws.amazon.com/cli/latest/reference/)，本方案原型对可能存在的命令差异不再做进一步说明。

将本方案原型代码克隆到本地：

```
git clone  https://github.com/weiping-bj/Smart-Sub-using-AWS.git
```

进入方案原型目录：

```
cd Smart-Sub-using-AWS
```

设置部署时需要用到的常量，```ACCOUNT_ID``` 和 ```BUCKET_NAME```：

```
ACCOUNT_ID=`aws sts get-caller-identity |jq -r ".Account"`

BUCKET_NAME=sc-poc-$ACCOUNT_ID
```

>如未安装 [jq](https://stedolan.github.io/jq/download/) 工具，也可以手工设置 ACCOUNT_ID

## 资源部署
### SNS Topic
本方案需创建 1 个 SNS 主题：```NotifyMe```。管理员订阅这个主题，并获知字幕处理结果的下载地址。

创建 SNS 主题：

```
NOTIFY_TOPIC_ARN=`aws sns create-topic --name NotifyMe --region us-east-1 | jq -r ".TopicArn"`

```

通过 AWS 控制台选择 ```Amazon SNS > 订阅 > 创建订阅```，输入网络管理员邮件地址，如下图：  
![TopicSubscription](png/03-Subscription.png "TopicSubscription")

需要通过管理员的邮箱确认上述订阅。

### S3 Bucket

创建 S3 Bucket：

```
aws s3api create-bucket --bucket $BUCKET_NAME \
--region us-east-1
```

创建成功后，返回 S3 Bucket 的 ARN。在 S3 Bucket  中创建 3 个目录。目录名称及作用说明如下：

- **input/**：用于保存需要处理的视频文件。

```
aws s3api put-object --bucket $BUCKET_NAME \
--key input/
```

- **inter-json/**：用于保存镜头识别和语音识别的中间信息。

```
aws s3api put-object --bucket $BUCKET_NAME \
--key inter-json/
```

- **result-json/**：用于保存按镜头分段的语音文本。

```
aws s3api put-object --bucket $BUCKET_NAME \
--key result-json/
```

### IAM Role








方案部署完成后，使用请参考 [使用说明](SmartSbu-usage-CHN.md)

[返回 README](README.md)