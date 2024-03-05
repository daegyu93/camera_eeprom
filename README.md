## Install requirements 

```bash
$ pip install -r requirements.txt
```

## read eeprom 

read_yaml_path : EEPROM 에서 읽어온 값을 저장할 yaml 파일 경로 
ex ) eeprom.yaml

```bash
$ python main -r [read_yaml_path] 
```

## write eeprom 

write_yaml_path : EEPROM에 쓸 값들이 들어있는 yaml 파일 경로 
ex ) parameter.yaml 

```bash
$ python main -w [write_yaml_path]
```

## -p option
read/ write 동일 아래와 같이 -p 옵션을 붙이면 read/write 한 parameter 내용들을 terminal 에 출력 

```bash
$ python main -r [read_yaml_path] -p 
```

## help 

```bash
$ python main.py -h
usage: main.py [-h] [-w WRITE] [-r READ] [-c CONFIG] [-p]

A simple program to demonstrate argument parsing

optional arguments:
  -h, --help            show this help message and exit
  -w WRITE, --write WRITE
                        Path to the yaml file for write eeprom
  -r READ, --read READ  Path to the yaml file for read eeprom
  -c CONFIG, --config CONFIG
                        Path to the yaml file for config eeprom
  -p, --print_result    Print the result
```

----
## 간단한 사용 예시 

1. 최초로 eeprom 을 read 하여 yaml 파일 하나를 만든다
2. 그 yaml 파일을 열어 필요한 부분에 값을 수정하고 write 한다
3. config 파일 내용을 기반으로 yaml 파일이 작성되고 eeprom 에 read/write 되니 특별한 상황이 아니면 config 파일은 건들지 않는다. 

eeprom.yaml 파일을 참조용으로 하나 첨부 드립니다. 
