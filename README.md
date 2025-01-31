# github 동기화
git add .

git commit -m "업데이트 내용 작성"

git push origin main(기본위치, 아니면 master)


# 동기화를 하지 않는 경우(용량이 큰 경우 등)
1. touch .gitignore 로 프로젝트 경로에 .gitignore 파일 생성
2. .gitignore에 제외할 파일, 폴더를 추가(main/ *.pyc 형식)

# 이미 동기화되어 삭제해야 하는 경우(github와 연결 전)
1. git rm -r --cached "폴더이름 폴더이름" 형식
2. 강제로 날리는 경우 git rm -r --cached -f "폴더이름 폴더이름"

# GIT 폴더를 변경하는 경우
1. 저장소를 확인 git remote -v
2. 새로운 저장소로 변경 git remote set-url origin "저장소 주소"
3. 변경 확인 git remote -v
4. 변경 내용 푸시 git push -u origin main

- 강제로 푸시하는 경우 git push --force origin main (기존 저장소 날아감)

# 라이브러리 설치
requirements.txt 참고

저장 pip freeze > requirements.txt

설치 pip install -r requirements.txt

# 음성파일 폴더
Player_eliminated_sound

# 가상환경
qr_pro1

- 발동 source /home/pi/Desktop/jener/winter_project/qr_pro1/bin/activate
- 해제 deactivate

# 제외폴더 _ .gitignore
- qr_pro1/
- Player_eliminated_sound/
- __pycache__/

- qrcode-learnopencv.jpg
