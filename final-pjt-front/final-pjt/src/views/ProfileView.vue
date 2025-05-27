<template>
  <v-container fluid class="mt-8">
    <!-- 네비게이션 바 -->
    <v-row><v-col cols="12"><NavigationBar/></v-col></v-row>

    <!-- 프로필 정보 보기 -->
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card elevation="2">
          <v-card-title class="text-h5">내 정보</v-card-title>
          <v-card-text>
            <v-list dense>
              <v-list-item>
                <v-list-item-title>ID</v-list-item-title>
                <v-list-item-subtitle>{{ form.username }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>이메일</v-list-item-title>
                <v-list-item-subtitle>{{ form.email }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>닉네임</v-list-item-title>
                <v-list-item-subtitle>{{ form.nickname }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>연령대</v-list-item-title>
                <v-list-item-subtitle>{{ form.age }}대</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn color="black" @click="goToEdit">회원정보 수정</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 북마크 차트 -->
    <v-row align="center" justify="center" class="mt-6">
     <v-col cols="12" sm="8" md="6">
       <!-- 예금 차트 -->
       <v-card elevation="2" class="pa-4 mb-6">
         <div class="text-h6 mb-4">가입한 예금 이율</div>
         <canvas ref="depositChart"></canvas>
       </v-card>

       <!-- 적금 차트 -->
       <v-card elevation="2" class="pa-4">
         <div class="text-h6 mb-4">가입한 적금 이율</div>
         <canvas ref="savingChart"></canvas>
       </v-card>
     </v-col>
   </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import { useAuthStore } from '@/stores/auth'
import NavigationBar from '@/components/NavigationBar.vue'
import apiClient from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

// 프로필
const form = ref({ username:'', email:'', nickname:'', age:'' })
const loading = ref(false)

// 차트 refs
const depositChart = ref(null)
const savingChart  = ref(null)

// 차트 인스턴스
let depositChartInstance = null
let savingChartInstance  = null

function goToEdit() {
  router.push({ name: 'profileEdit' })
}

onMounted(async () => {
  loading.value = true
  try {
    // --- 1) 프로필 불러오기 ---
    const { data: user } = await apiClient.get('/accounts/user/')
    form.value = {
      username: user.username,
      email:    user.email,
      nickname: user.nickname,
      age:      user.age
    }

    // --- 2) 북마크 예금/적금 불러오기 ---
    const depRes = await apiClient.get(
      '/bookmarks/deposits/',
      { headers: { Authorization: `Token ${auth.token}` } }
    )
    const savRes = await apiClient.get(
      '/bookmarks/savings/',
      { headers: { Authorization: `Token ${auth.token}` } }
    )
    const deposits = Array.isArray(depRes.data)
      ? depRes.data
      : depRes.data.results || []
    const savings  = Array.isArray(savRes.data)
      ? savRes.data
      : savRes.data.results || []

    // --- 3) 차트용 데이터 가공 ---
    const depLabels = [], depR1 = [], depR2 = []
    deposits.forEach(bm => {
      const p = bm.deposit_product
      depLabels.push(p.fin_prdt_nm)
      if (p.options.length) {
        console.log(p.options)
       const best = p.options.reduce((a, b) =>
         (a.intr_rate2 ?? 0) > (b.intr_rate2 ?? 0) ? a : b
       )
       depR1.push(best.intr_rate ?? 0)
       depR2.push(best.intr_rate2 ?? 0)
     } else {
       depR1.push(0)
       depR2.push(0)
     }
    })

    const savLabels = [], savR1 = [], savR2 = []
    savings.forEach(bm => {
      const p = bm.saving_product
      savLabels.push(p.fin_prdt_nm)
      if (p.options.length) {
        savR1.push(p.options[0].intr_rate)
        savR2.push(p.options[0].intr_rate2)
      } else {
        savR1.push(0); savR2.push(0)
      }
    })

    // --- 4) 차트 렌더링 ---
    await nextTick()
    depositChartInstance = new Chart(depositChart.value, {
      type: 'bar',
      data: {
        labels: depLabels,
        datasets: [
          { label:'저축 금리', data: depR1, backgroundColor:'rgba(54,162,235,0.5)' },
          { label:'최고 우대 금리', data: depR2, backgroundColor:'rgba(75,192,192,0.5)' },
        ]
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true, title:{display:true,text:'%'} } }
      }
    })

    savingChartInstance = new Chart(savingChart.value, {
      type: 'bar',
      data: {
        labels: savLabels,
        datasets: [
          { label:'저축 금리', data: savR1, backgroundColor:'rgba(255,159,64,0.5)' },
          { label:'최고 우대 금리', data: savR2, backgroundColor:'rgba(153,102,255,0.5)' },
        ]
      },
      options: {
        responsive: true,
        scales:{ y:{ beginAtZero:true, title:{display:true,text:'%'} } }
      }
    })

  } catch(e) {
    console.error(e)
    auth.clearAuth()
    router.push({ name: 'login' })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* v-btn 오버라이드 불필요 */
</style>
