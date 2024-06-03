import openai
from openai import OpenAIError
import warnings
from transformers import GPT2Tokenizer

warnings.simplefilter(action='ignore', category=FutureWarning)

openai.api_key = ''
MAX_TOKEN_LENGTH = 3800

question = '''
당신의 임무는 제공되는 디렉토리를 분석하고, 그 후 주어진 본문을 어떤 디렉토리에 저장할지 결정하는 것입니다. 출력 형식은 다음과 같습니다. (<디렉토리의 이름>, ID: 디렉토리 id)
디렉토리는 다음과 같은 형식으로 주어집니다. 
"|-- 디렉토리의 이름, (ID: 디렉토리 id)"
입력된 본문을 분석하고, 가장 저장하기 적합한 디렉토리를 선택한 후 디렉토리의 이름과 id를 출력하세요.

1. 주어진 디렉토리 중 본문과 가장 연관성이 높은 디렉토리를 선택하세요.
2. 연관성이 있는 디렉토리가 없다고 판단되면, 해당 본문을 기반으로 한 단어로 요약한 것ㅎ을 바탕으로 디렉토리 이름 을 만들어야합니다. 이 때, 만든 디렉토리의 이름은 기존에 존재하는 디렉토리의 이름과 겹치지 않아야 합니다.

디렉토리 이름은 한글로만 구성되어야 하며, 1글자 이상 20글자 이하로 구성되어야 합니다. 디렉토리 이름은 공백을 포함하지 않아야 합니다.

출력 형식은 다음과 같습니다. (<디렉토리의 이름>, ID: 디렉토리 id) 
만일 새로운 디렉토리를 만들었다면, ID는 상위 디렉토리의 id를 사용하세요. 만일 연관된 디렉토리가 없다면, id는 null로 출력하세요.
만일 기존의 디렉토리를 선택했다면, 디렉토리 이름은 null, 디렉토리 id는 선택한 디렉토리의 id를 출력하세요.
반드시 (<디렉토리의 이름>, ID: 디렉토리id)만을 출력하도록 하세요. 여기서 <디렉토리의 이름> 부분은 반드시 다른 단어로 대체하여야 합니다. 다른것은 절대 출력해서는 안됩니다. 예를들어, "출력 결과" 라던지, "---"등의 문자열은 출력해서는 안됩니다.
만일 출력물에 "디렉토리"라는 단어가 들어간다면, 다시 수행하세요.

이제부터 디렉토리 목록과 본문을 제공하겠습니다. 전부 확실하게 확인한 후, 위에서 설명한 임무를 수행하세요.
'''


def process_directory(directory, content: str) -> str:
    results = []
    request = question + directory + content

    response = openai.ChatCompletion.create(
        model='gpt-4o',
        max_tokens=300,
        messages=[{"role": "user", "content": request}]
    )    

    chat_response = response.choices[0].message.content
    directory_str, id_str = parse_response(chat_response)
    
    return directory_str, id_str

def parse_response(response: str) -> tuple:
    if response.startswith('(') and response.endswith(')'):
        response = response[1:-1]
    directory_str, id_part = response.split(", ID:")
    if directory_str.startswith('<')and directory_str.endswith('>'):
        directory_str = directory_str[1:-1]
    return directory_str.strip(), id_part.strip()

"""def testDirectory():
    directory = "|--개발,(ID: 123)\n    |--백엔드,(ID: 456)\n       |--restapi,(ID: 789)\n  |--프론트엔드,(ID: 234)\n|--여행,(ID: 567)\n|--경제,(ID: 345)\n|--노래,(ID: 678)\n"
    content = "목요일인 23일은 전국 대부분 지역에서 낮 기온이 25도 이상 오르면서 덥겠고, 대구는 32도까지 오르며 한여름 날씨를 보일 전망이다. 전국은 대체로 맑겠으나 서해안과 수도권‧충청권‧전북내륙에는 오전 사이 짙은 안개가 끼는 곳이 있겠다.\
        기상청에 따르면 이날 아침 최저 기온은 12~22도, 낮 최고기온은 22도~32도가 되겠다.주요 도시별 최저기온은 △서울 16도 △인천 15도 △춘천 13도 △철원 12도 △원주 15도 △강릉 22도 △대전 16도 △세종 15도 △대구 17도 △부산 18도 △광주 \
            17도 △제주 18도 등이다.낮 최고기온은 △서울 26도 △인천 22도 △춘천 28도 △철원 27도 △원주 28도 △강릉 31도 △대전 29도 △세종 29도 △대구 32도 △부산 26도 △광주 29도 △제주 24도 등이다.안개는 오전 사이 서해안과 수도권‧충청\
                권‧전북내륙에는 가시거리 200m 미만의 짙은 안개가 끼는 곳이 있겠고, 일부 지역에는 이슬비가 내리는 곳도 있겠다.미세먼지는 전 권역이 좋음 또는 보통으로 예상된다. 다만 서울·경기남부·충남은 오전에 일시적으로 '나쁨' 수준을 보일 전\
                    망이다.기상청 관계자는 \"해안에 위치한 교량(서해대교와 인천대교, 영종대교, 천사대교 등)과 내륙의 강이나 호수, 골짜기에 인접한 도로에서는 주변보다 안개가 더욱 짙게 끼는 곳이 있겠으니 교통안전에 각별히 유의할 필요가 있다\"\
                        고 당부했다"
    print(process_directory(directory, content))

def testDirectory2():
    directory = "|--개발,(ID: 123)\n    |--백엔드,(ID: 456)\n       |--restapi,(ID: 789)\n  |--프론트엔드,(ID: 234)\n|--여행,(ID: 567)\n|--경제,(ID: 345)\n|--노래,(ID: 678)\n"
    content = "API(Application Programming Interface)란?API는 애플리케이션 소프트웨어를 구축하고 통합하기 위한 정의 및 프로토콜 세트로, 때때로 API는 정보 제공자와 정보 사용자 간의 계약으로 지칭되며 소비자에게 필요한 콘텐츠(호출)와 생산자\
        에게 필요한 콘텐츠(응답)를 구성합니다.예를 들어, 날씨 서비스용 API 설계에서는 사용자는 우편번호를 제공하고, 생산자는 두 부분(첫 번째는 최고 기온, 두 번째는 최저 기온)으로 구성된 응답으로 답하도록 지정할 수 있습니다.  바꿔 말하자면 컴\
            퓨터나 시스템과 상호 작용하여 정보를 검색하거나 기능을 수행하고자 할 때 API는 사용자가 원하는 것을 시스템에 전달할 수 있게 지원하여 시스템이 이 요청을 이해하고 이행하도록 할 수 있습니다. API를 사용자 또는 클라이언트, 그리고 사용자\
                와 클라이언트가 얻으려 하는 리소스 또는 웹 서비스 사이의 조정자로 생각하면 됩니다. API는 조직이 보안, 제어, 인증을 유지 관리(누가 무엇에 액세스할 수 있는지 결정)하면서 리소스와 정보를 공유할 수 있는 방법이기도 합니다. API의 \
                    또 다른 장점은 캐싱, 즉 리소스 검색 방법 또는 리소스의 출처에 대해 자세히 알 필요가 없다는 것입니다."
    print(process_directory(directory, content))

testDirectory()
testDirectory2()"""