///https://discord.com/oauth2/authorize?client_id=1226179101748887683&scope=bot&permissions=1099511627775
// Создаем объект клиента Discord
const { Client, GatewayIntentBits, Partials, MessageEmbed, MessageActionRow, MessageButton } = require('discord.js');
const client = new Client({ 
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.MessageContent], 
    partials: [Partials.GUILD_MEMBER] 
});

// Событие готовности бота
client.once('ready', () => {
    console.log('Бот готов!');
    // Получаем первый доступный сервер
    const guild = client.guilds.cache.first();
    if (guild) {
        // Получаем канал по его ID
        const channel = guild.channels.cache.get('1135614238937858189');
        if (channel) {
            // Отправляем сообщение в канал
          
        } else {
            console.log('Не удалось найти канал с ID 1135614238937858189.');
        }
    } else {
        console.log('Не удалось найти сервер.');
    }
});

// Событие взаимодействия с кнопкой
client.on('interactionCreate', (interaction) => {
    if (interaction.isButton()) {
        if (interaction.customId === 'pyk_button') {
            // Создаем эмбед с надписью "Я ПИДОРАС"
            const embed = new MessageEmbed()
                .setTitle('Я ПИДОРАС')
                .setDescription('Большими буквами');

            // Отвечаем на взаимодействие с новым эмбедом
            interaction.reply({ embeds: [embed] });
        }
    }
});

// Событие при получении сообщения
client.on('messageCreate', (message) => {
    if (message.content === '.pyk') {
        // Создаем красивый эмбед
        const embed = new MessageEmbed()
            .setTitle('Красивый эмбед')
            .setDescription('Нажми на кнопку ниже');

        // Создаем кнопку
        const button = new MessageButton()
            .setCustomId('pyk_button')
            .setLabel('Нажми меня')
            .setStyle('PRIMARY');

        // Создаем строку с кнопкой
        const row = new MessageActionRow()
            .addComponents(button);

        // Отправляем сообщение с эмбедом и кнопкой
        message.channel.send({ embeds: [embed], components: [row] });
    }
});





// Включаем бота с использованием токена
client.login('MTIyNjE3OTEwMTc0ODg4NzY4Mw.GTlqk3.2uPY62wVuN5myawZ-Hs6KPqSS0s4w0wI2r8lDo');
