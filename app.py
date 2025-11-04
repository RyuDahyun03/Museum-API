# Museum-API

import streamlit as st
import requests

# Met API 기본 URL
SEARCH_API_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT_API_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

# Streamlit 앱 제목 설정
st.set_page_config(page_title="뮤지엄 아트워크 검색기", layout="wide")
st.title("🏛️ 뮤지엄 아트워크 검색기 (The Met API)")

# 검색어 입력창
search_query = st.text_input(
    "검색어를 입력하세요 (예: Van Gogh, cats, monet...)",
    help="찾고 싶은 작품의 키워드나 작가 이름을 영어로 입력해 주세요."
)

if search_query:
    # 1. 검색 API 호출
    with st.spinner(f"'{search_query}'(으)로 작품을 검색 중입니다..."):
        try:
            search_response = requests.get(SEARCH_API_URL, params={"q": search_query, "hasImages": "true"})
            search_response.raise_for_status()  # 오류 발생 시 예외 처리
            search_data = search_response.json()

            object_ids = search_data.get("objectIDs")

            if not object_ids:
                st.warning("검색 결과가 없습니다. 다른 키워드로 시도해 보세요.")
            else:
                st.success(f"총 {search_data.get('total', 0)}개의 작품을 찾았습니다. (최대 12개까지 표시)")
                
                # 결과가 너무 많을 수 있으므로 일부만 (예: 최대 12개) 가져옵니다.
                object_ids_to_show = object_ids[:12]

                # (수정) 3단 그리드 컬럼을 생성하는 대신, 각 아이템별로 컬럼을 생성합니다.
                # 아래 두 줄을 삭제합니다.
                # cols = st.columns(3)
                # col_index = 0

                for object_id in object_ids_to_show:
                    # 2. 개별 작품 정보 API 호출
                    try:
                        object_response = requests.get(f"{OBJECT_API_URL}{object_id}")
                        object_response.raise_for_status()
                        object_data = object_response.json()

                        # 작품 이미지, 제목, 작가, 링크 표시
                        image_url = object_data.get("primaryImageSmall")
                        title = object_data.get("title", "제목 없음")
                        artist = object_data.get("artistDisplayName", "작가 미상")
                        object_url = object_data.get("objectURL", "#")

                        if image_url:
                            # (수정) 잡지 스타일 레이아웃을 위해 2개의 열을 생성합니다.
                            # 이미지:설명 = 1:2 비율로 설정
                            img_col, desc_col = st.columns([1, 2])

                            with img_col:
                                st.image(image_url, caption=f"'{title}' by {artist}", use_column_width=True)
                            
                            with desc_col:
                                st.markdown(f"**[{title}]({object_url})**")
                                st.write(f"**작가:** {artist}")
                                st.write(f"**연도:** {object_data.get('objectDate', '미상')}")
                                # (추가) 더 많은 설명 정보를 넣을 수 있습니다.
                                st.write(f"**매체:** {object_data.get('medium', '미상')}")
                                st.write(f"**부서:** {object_data.get('department', '미상')}")

                            # (추가) 각 작품 사이에 구분선을 추가합니다.
                            st.markdown("---")
                            
                            # (수정) col_index 관련 로직 삭제
                            # col_index = (col_index + 1) % 3

                    except requests.exceptions.RequestException as e:
                        # 개별 작품 로드 실패 시
                        st.error(f"작품 ID {object_id} 로드 중 오류 발생: {e}")

        except requests.exceptions.RequestException as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")

