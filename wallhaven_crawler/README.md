# wallhaven crawler
爬取[Wallhaven](https://alpha.wallhaven.cc)的图片

## 1. 爬取榜单图片
```shell
python wallhaven_image top_list -p ${last_page_number}
```

## 2. 爬取最近浏览图片
```shell
python wallhaven_image latest -p ${last_page_number} 
```

## 3. 爬取搜索关键词图片
```shell
python wallhaven_image query -v ${query value} -p ${last_page_number} 
```

## 4. 爬取随机图片
```shell
python wallhaven_image random -p ${last_page_number} 
```

> -p 可选,默认爬取前10页图片,已爬取过的图片链接会存库,不会再爬取