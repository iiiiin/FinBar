const fetchRecommendations = async () => {
  try {
    loading.value = true
    const response = await axios.get(
      `${import.meta.env.VITE_API_BASE_URL}/api/suggests/investment-product-recommendation/`,
      {
        headers: {
          Authorization: `Token ${token}`,
        },
        timeout: 30000, // 30초로 타임아웃 증가
      }
    )
    recommendations.value = response.data
    console.log("추천 상품 데이터:", recommendations.value)
  } catch (error) {
    console.error("추천 상품 조회 실패:", error)
    if (error.code === "ECONNABORTED") {
      alert("서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
    } else {
      alert("추천 상품을 불러오는데 실패했습니다.")
    }
  } finally {
    loading.value = false
  }
} 