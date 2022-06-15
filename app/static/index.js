class TextDownload {
    		// 클래스 생성자 초기화 실시
    		constructor(data="") {
    			this.data = data;
    		}
    		// 파일 다운로드 수행 실시
            download (type_of = "text/plain", filename = "d.txt") { // 확장자명을 txt 으로 지정
    			let body = document.body; // body 변수 선언
    			const a = document.createElement("a"); // a 태그 생성
    			a.href = URL.createObjectURL(new Blob([this.data], {
    				type: type_of
    			}));
    			a.setAttribute("download", filename); // a 태그에 다운로드 속성 추가
    			body.appendChild(a); // body에 a 태그 추가
    			a.click(); // 클릭 이벤트를 발생시켜 다운로드
    			body.removeChild(a); // body에서 제거
    		}
    	};

function thumbnail(input) {
    let fileinfo = document.getElementById("chooseFile").files[0];
    let reader = new FileReader();

    reader.onload = function() {
        document.getElementById("thumbnailImg").src = reader.result;
    }

    if (fileinfo) {
        reader.readAsDataURL( fileinfo );
    }

}

function saveText(){
    new TextDownload(document.getElementById("chooseFile").value).download();
}


