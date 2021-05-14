# AWS-AI-Services-in-Media-Industry

AWS 推出了一系列 [AI 相关](https://aws.amazon.com/cn/machine-learning/ai-services/) 的服务。其中的一些服务与其它 AWS 服务相结合，可以组合出适应特定媒体场景需求的方案。在此列出一些个人曾经实现过的功能原型：

## [快速截取视频片段](quick-clips/QuickClips-deploy-CHN.md)：  

- **场景说明**：视频文件保存在 S3 存储桶中，需要获取其中的一个片段到本地进行编辑。
- **方案说明**：利用 MediaConvert 服务直接对 S3 存储桶中的视频进行片段截取。
- **方案收益**：减少从云上下载文件时的流量费用。
