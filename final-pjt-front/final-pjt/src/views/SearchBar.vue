<!-- components/SearchBar.vue -->
<template>
    <v-row align="center" class="search-bar--inline" no-gutters>
      <v-col class="pr-2">
        <v-text-field
          v-model="searchText"
          dense
          outlined
          placeholder="검색어를 입력하세요"
          @keyup.enter="onSearch"
        />
      </v-col>
      <!-- <v-col class="shrink">
        <v-btn color="primary" @click="onSearch">검색</v-btn>
      </v-col> -->
    </v-row>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  
  const props = defineProps({ modelValue: String })
  const emits = defineEmits(['update:modelValue','search'])
  
  const searchText = ref(props.modelValue)
  watch(() => props.modelValue, v => searchText.value = v)
  watch(searchText, v => emits('update:modelValue', v))
  
  function onSearch(){ emits('search') }
  </script>
  
  <style scoped>
  .search-bar--inline {
    display: flex;
    align-items: center;
  }
  .search-bar--inline .v-col.shrink {
    flex: 0 0 auto;
  }
  </style>
  