# AWS-AI-Services-in-Media-Industry

AWS 推出了一系列 [AI 相关](https://aws.amazon.com/cn/machine-learning/ai-services/) 的服务。其中的一些服务与其它 AWS 服务相结合，可以组合出适应特定媒体场景需求的方案。在此列出一些个人曾经实现过的功能原型：

## [快速截取视频片段](https://github.com/weiping-bj/Quick-Clips-with-AWS-MediaConvert)：  

- **场景说明**：视频文件保存在 S3 存储桶中，需要获取其中的一个片段到本地进行编辑。
- **方案说明**：利用 MediaConvert 服务直接对 S3 存储桶中的视频进行片段截取。
- **方案收益**：减少从云上下载文件时的流量费用。

## [基于人脸识别技术的快速剪辑](https://github.com/weiping-bj/Smart-Cutting-using-AWS)：

- **场景说明**：搜索视频，提取出所有包含特定人脸信息的视频片段，并剪辑成一个新的视频。
- **方案说明**：利用 Rekognition 进行人脸识别和时间码提取，利用 MediaConvert 进行视频剪辑与合成。
- **方案收益**：提高人脸识别准确率，减少视频合辑生成的时间。 

## [自动获取宣讲视频中每页 PPT 的讲解词](https://github.com/weiping-bj/Smart-ASR-on-PPT-Pages) 

- **场景说明**：在线宣讲视屏中，画面是 PPT 播放，声音是演讲者的语音。本方案可以根据 PPT 的换页时间，自动将宣讲者在每页 PPT 中的讲解转录成文本信息。
- **方案说明**：利用 Rekognition 识别 PPT 的换页起止时间。依据提取好的时间片段，对 Transcribe 转录出的文本元素进行组合，生成分好片段的文本。
- **方案收益**：回看者根据文本信息即可快速定位到具体的某页 PPT 播放的时间点，提高观看效率。

## [利用镜头识别技术对视频快速拆条](code/auto-video-seg.py)

- **场景说明**：以镜头的切换为单位，对长视频快速拆条成多个短视频片段。
- **方案说明**：利用 Rekognition 的镜头识别功能对视频中镜头的切换时间进行提取，利用 MediaConvert 服务基于提取出的镜头起止时间进行视频的自动切分，将一个长视频切分成多个短视频。可从 [此处](code/auto-video-seg.py) 查看代码，MediaConvert 使用 [作业模板](code/auto-video-seg-job-template.json) 作为创建作业的参数。
- **方案收益**：快速实现长视频拆条，提高段视频生产效率。

## [中文数字转阿拉伯数字](code/Number2Digit.py)

- **场景说明**：部分 ASR 服务在提取中文文本信息时，数字将以文字形式进行提取（例如：三点一四一五九二六）。本方案将文字数字转换成阿拉伯数字。
- **方案说明**：针对一句话中的数字信息进行检索，对以下文字数字进行转换：
    1. 包括亿、千亿、万亿等；
    2. 整点的时间不进行转换；
    3. 单独出现的一位数字不进行转换，例如：一心一意，天下第一关；
    4. 叠字出现的数字位不进行转换，例如：亿万，千千万万；
    5. 包含小数点时，小于5位的不进行转换，例如：十二点零五，三点零九（重要是为了避免时间的误转，所以类似三点零五这种小数也不转换了）；
    6. 支持大数缩写的转换，例如：二十八亿，三点六万，转写成 28亿，3.6万
    7. 支持对口语表达的转换，例如：二万五，转写成 25000，而不是 20005
- **方案收益**：提升 ASR 结果的可读性。