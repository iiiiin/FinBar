<template>
  <v-container class="mx-auto" :style="{ maxWidth: '800px' }">
    <!-- 네비게이션 바 -->
    <v-row>
      <v-col cols="12">
        <NavigationBar />
      </v-col>
    </v-row>

    <!-- 페이지 제목 -->
    <v-row class="my-4">
      <v-col cols="12">
        <Title :title="pageTitle" />
      </v-col>
    </v-row>

    <!-- 금/은 토글 + 날짜 선택 -->
    <v-row class="mb-4" align="center">
      <v-col cols="4">
        <v-btn
          block
          :color="selected === 'gold' ? 'warning' : 'grey'"
          @click="selected = 'gold'"
        >
          금
        </v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn
          block
          :color="selected === 'silver' ? 'info' : 'grey'"
          @click="selected = 'silver'"
        >
          은
        </v-btn>
      </v-col>
      <v-col cols="2">
        <v-menu
          v-model="startMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          min-width="auto"
        >
        <template #activator="{ props }">
          <v-text-field
            v-model="startDate"
            label="시작일 선택"
            readonly
            v-bind="props"/>
        </template>
          <v-date-picker
            v-model="startDate"
            @input="startMenu = false"
            locale="ko-kr"
          />
        </v-menu>
      </v-col>
      <v-col cols="2">
        <v-menu
          v-model="endMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          min-width="auto"
        >
          <template #activator="{ props }">
            <v-text-field
              v-model="endDate"
              label="종료일 선택"
              readonly
              v-bind="props"/>
          </template>
          <v-date-picker
            v-model="endDate"
            @input="endMenu = false"
            locale="ko-kr"
          />
        </v-menu>
      </v-col>
    </v-row>

    <!-- 가격 변동 그래프 -->
    <v-row>
      <v-col cols="12">
        <Line
          v-if="chartData"
          :data="chartData"
          :options="chartOptions"
          style="height: 400px;"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
// Chart.js core + 레지스터블 전부 불러와서 한 번에 등록
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)
import { Line } from 'vue-chartjs'
// SheetJS 최신 권장 import 방식 (named imports)
import { read, utils } from 'xlsx'

import NavigationBar from '@/components/NavigationBar.vue'
import Title         from '@/components/Title.vue'

const pageTitle = '금/은 가격 변동'
const selected  = ref('gold')

const startDate = ref('')
const endDate   = ref('')
const startMenu = ref(false)
const endMenu   = ref(false)

const chartData = ref({
  labels: [],
  datasets: [{
    label: '',
    data: [],
    fill: false,
    borderWidth: 2
  }]
})
const chartOptions = {
  responsive: true,
  elements: {
    line: {
      tension: 0.4
    }
  },
  scales: {
    x: { title: { display: true, text: 'Date' } },
    y: { title: { display: true, text: 'Price' }, beginAtZero: false }
  }
}

// Excel serial → JS Date 변환 함수
function excelDateToJSDate(serialStr) {
  const serial = Number(serialStr);
  if (Number.isNaN(serial)) {
    console.warn(`Invalid Excel serial: ${serialStr}`);
    return null;
  }
  // Excel은 1900-01-00을 day 0으로 계산 (윤년 버그 포함)
  const utc_days = serial - 25569;
  const ms       = utc_days * 86400 * 1000;
  return new Date(ms);
}

async function loadData() {
  const fileName = selected.value === 'gold'
    ? 'Gold_prices.xlsx'
    : 'Silver_prices.xlsx'
  const resp = await fetch(`/data/${fileName}`)
  if (resp.status !== 200) throw new Error(`파일 로드 실패: ${resp.status}`)
  const arrayBuffer = await resp.arrayBuffer()

  // 최신 read/SheetJS API 사용 :contentReference[oaicite:0]{index=0}
  const workbook = read(arrayBuffer)
  const sheet    = workbook.Sheets[workbook.SheetNames[0]]
  const rows     = utils.sheet_to_json(sheet, { header: 1, raw: true })

  const header   = rows[0].map(h => String(h).trim())
  const dateIdx  = header.indexOf('Date')
  const closeIdx = header.indexOf('Close/Last')
  // if (dateIdx < 0 || closeIdx < 0) return

  const rawDates = rows.slice(1).map(r => String(r[dateIdx]))

  // console.log('🔖 Excel Date Column:', typeof rawDates[0])

  const isoDates = rawDates.map(serialStr => {
    // 1) 문자열을 숫자로 변환한 뒤 Date 객체 생성
    const dt = excelDateToJSDate(serialStr);
    if (dt instanceof Date && !isNaN(dt)) {
      // 2) 성공적으로 Date 객체가 만들어졌으면 ISO YYYY-MM-DD 문자열로
      return dt.toISOString().split('T')[0];
    }
    // 3) 변환 실패 시, 원본 문자열 그대로(또는 원하는 대체값)
    console.warn(`Invalid serial for date conversion: ${serialStr}`);
    return null;  // 혹은 '' 등
    });

  
  
  // 1) Date 문자열 파싱 + ISO 포맷으로 변환, 2) 원본 Date 객체도 함께 저장
  let data = isoDates.map((label, i) => {
    const rawRow = rows[i+1]
    // 1) 쉼표 제거한 문자열
    const rawVal = String(rawRow[closeIdx])
    const numStr = rawVal.replace(/,/g, '')
    const parsedValue  = parseFloat(numStr)
    return {
      dateObj: new Date(label),
      label,
      parsedValue
    }
  })

  // 시작/종료일 필터 (v-date-picker의 value는 "YYYY-MM-DD" 포맷)
  if (startDate.value) {
    data = data.filter(d => d.dateObj >= new Date(startDate.value))
  }

  if (endDate.value) {
    data = data.filter(d => d.dateObj <= new Date(endDate.value))
  }

  data.sort((a, b) => a.dateObj - b.dateObj)
  chartData.value = {
    labels: data.map(d => d.label),
    datasets: [{
      label: selected.value === 'gold' ? '금 시세' : '은 시세',
      data: data.map(d => d.parsedValue),
      fill: false,
      borderColor: selected.value === 'gold' ? '#f1c40f' : '#95a5a6',
      borderWidth: 2
    }]
  }
}

watch([selected, startDate, endDate], loadData)
onMounted(loadData)
</script>

<style scoped>
/* 필요 시 추가 스타일 */
</style>
 