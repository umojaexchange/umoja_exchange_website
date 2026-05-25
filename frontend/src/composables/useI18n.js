import {ref} from 'vue'

const lang = ref(localStorage.getItem('umoja_lang') || 'en')

const dict = {
    en: {
        // Nav
        dashboard: 'Dashboard', purchases: 'Purchases', sales: 'Sales',
        reports: 'Reports', settings: 'Settings', logout: 'Logout',
        // Dashboard
        totalCapital: 'Total Capital', remainingInventory: 'Remaining Inventory',
        totalProfit: 'Total Profit', totalCustomers: 'Total Customers',
        totalPurchases: 'Total Purchases', totalSales: 'Total Sales',
        dailyProfit: 'Daily Profit', weeklyProfit: 'Weekly Profit',
        monthlyProfit: 'Monthly Profit', annualProfit: 'Annual Profit',
        profitTrend: 'Profit Trend', paymentMethods: 'Payment Methods',
        monthlyOverview: 'Monthly Overview', capitalWarning: 'Capital is at or below minimum threshold',
        daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly', annual: 'Annual',
        revenue: 'Revenue', profit: 'Profit',
        // Purchases
        addPurchase: 'Add Purchase', editPurchase: 'Edit Purchase',
        supplier: 'Supplier', supplierName: 'Supplier Full Name',
        usdtAmount: 'USDT Amount', rateTZS: 'Rate in TZS',
        amountPaid: 'Amount Paid (TZS)', paymentMethod: 'Payment Method', notes: 'Notes',
        totalUSDTBought: 'Total USDT Bought', totalSpent: 'Total Spent',
        todayPurchases: "Today's Purchases", remainingStock: 'Remaining Stock',
        // Sales
        newSale: 'New Sale', customer: 'Customer', customerName: 'Customer Full Name',
        saleRate: 'Sale Rate (TZS)', avgBuyRate: 'Avg Buy Rate',
        profitMargin: 'Profit Margin', totalUSDTSold: 'Total USDT Sold',
        totalRevenue: 'Total Revenue', todaySales: "Today's Sales",
        // Common
        search: 'Search...', filter: 'Filter', clearFilters: 'Clear', all: 'All',
        dateFrom: 'Date From', dateTo: 'Date To', actions: 'Actions',
        edit: 'Edit', delete: 'Delete', save: 'Save', cancel: 'Cancel',
        showing: 'Showing', of: 'of', records: 'records', noData: 'No data found',
        previous: 'Prev', next: 'Next', deleteConfirm: 'Delete this record?',
        cannotUndo: 'This action cannot be undone.', today: 'Today',
        // Auth
        signIn: 'Sign In', username: 'Username', password: 'Password',
        signingIn: 'Signing in...', welcomeBack: 'Welcome back',
        signInToContinue: 'Sign in to your account to continue',
        // Settings
        saveSettings: 'Save Settings', minRate: 'Minimum Rate (TZS)',
        maxRate: 'Maximum Rate (TZS)', minAsset: 'Minimum Asset (USDT)',
        maxAsset: 'Maximum Asset (USDT)', companyCapital: 'Company Capital (TZS)',
        minThreshold: 'Minimum Threshold (TZS)', reportEmail: 'Report Email',
        capitalMonitoring: 'Capital Monitoring', rateLimits: 'Rate Limits',
        assetLimits: 'Asset Limits', notifications: 'Notifications',
        lastUpdated: 'Last updated', readOnly: 'Read-only. Contact admin to change.',
        // Reports
        purchaseReport: 'Purchase Report', salesReport: 'Sales Report',
        exportPDF: 'Export PDF', exportExcel: 'Export Excel',
        generating: 'Generating...',
        fifoBreakdown: 'FIFO Breakdown',
    },
    sw: {
        // Nav
        dashboard: 'Dashibodi', purchases: 'Manunuzi', sales: 'Mauzo',
        reports: 'Ripoti', settings: 'Mipangilio', logout: 'Toka',
        // Dashboard
        totalCapital: 'Mtaji Wote', remainingInventory: 'Hesabu Iliyobaki',
        totalProfit: 'Faida Yote', totalCustomers: 'Wateja Wote',
        totalPurchases: 'Manunuzi Yote', totalSales: 'Mauzo Yote',
        dailyProfit: 'Faida ya Leo', weeklyProfit: 'Faida ya Wiki',
        monthlyProfit: 'Faida ya Mwezi', annualProfit: 'Faida ya Mwaka',
        profitTrend: 'Mwenendo wa Faida', paymentMethods: 'Njia za Malipo',
        monthlyOverview: 'Muhtasari wa Mwezi', capitalWarning: 'Mtaji uko chini ya kiwango cha chini',
        daily: 'Kila Siku', weekly: 'Kila Wiki', monthly: 'Kila Mwezi', annual: 'Kila Mwaka',
        revenue: 'Mapato', profit: 'Faida',
        // Purchases
        addPurchase: 'Ongeza Ununuzi', editPurchase: 'Hariri Ununuzi',
        supplier: 'Muuzaji', supplierName: 'Jina Kamili la Muuzaji',
        usdtAmount: 'Kiasi cha USDT', rateTZS: 'Kiwango kwa TZS',
        amountPaid: 'Kiasi Kilicholipwa (TZS)', paymentMethod: 'Njia ya Malipo', notes: 'Maelezo',
        totalUSDTBought: 'USDT Iliyonunuliwa', totalSpent: 'Jumla Iliyotumika',
        todayPurchases: 'Manunuzi ya Leo', remainingStock: 'Hesabu Iliyobaki',
        // Sales
        newSale: 'Uuzaji Mpya', customer: 'Mteja', customerName: 'Jina Kamili la Mteja',
        saleRate: 'Kiwango cha Uuzaji (TZS)', avgBuyRate: 'Wastani wa Kununua',
        profitMargin: 'Faida ya Mauzo', totalUSDTSold: 'USDT Iliyouzwa',
        totalRevenue: 'Mapato Yote', todaySales: 'Mauzo ya Leo',
        // Common
        search: 'Tafuta...', filter: 'Chuja', clearFilters: 'Futa', all: 'Yote',
        dateFrom: 'Tarehe ya Kuanzia', dateTo: 'Tarehe ya Mwisho', actions: 'Vitendo',
        edit: 'Hariri', delete: 'Futa', save: 'Hifadhi', cancel: 'Ghairi',
        showing: 'Inaonyesha', of: 'kati ya', records: 'rekodi', noData: 'Hakuna data',
        previous: 'Iliyopita', next: 'Inayofuata', deleteConfirm: 'Futa rekodi hii?',
        cannotUndo: 'Kitendo hiki hakiwezi kutenduliwa.', today: 'Leo',
        // Auth
        signIn: 'Ingia', username: 'Jina la Mtumiaji', password: 'Nenosiri',
        signingIn: 'Inaingia...', welcomeBack: 'Karibu tena',
        signInToContinue: 'Ingia kwenye akaunti yako kuendelea',
        // Settings
        saveSettings: 'Hifadhi Mipangilio', minRate: 'Kiwango cha Chini (TZS)',
        maxRate: 'Kiwango cha Juu (TZS)', minAsset: 'Mali ya Chini (USDT)',
        maxAsset: 'Mali ya Juu (USDT)', companyCapital: 'Mtaji wa Kampuni (TZS)',
        minThreshold: 'Kiwango cha Chini (TZS)', reportEmail: 'Barua pepe ya Ripoti',
        capitalMonitoring: 'Ufuatiliaji wa Mtaji', rateLimits: 'Mipaka ya Kiwango',
        assetLimits: 'Mipaka ya Mali', notifications: 'Arifa',
        lastUpdated: 'Ilisasishwa', readOnly: 'Soma tu. Wasiliana na msimamizi kubadilisha.',
        // Reports
        purchaseReport: 'Ripoti ya Manunuzi', salesReport: 'Ripoti ya Mauzo',
        exportPDF: 'Pakua PDF', exportExcel: 'Pakua Excel',
        generating: 'Inaunda...',
        fifoBreakdown: 'Uchambuzi wa FIFO',
    }
}

export function useI18n() {
    const t = (key) => dict[lang.value]?.[key] ?? dict.en[key] ?? key
    const setLang = (l) => {
        lang.value = l;
        localStorage.setItem('umoja_lang', l)
    }
    const toggleLang = () => setLang(lang.value === 'en' ? 'sw' : 'en')
    return {t, lang, setLang, toggleLang}
}
