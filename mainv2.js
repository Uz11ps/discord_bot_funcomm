const Discord = require('discord.js');
const client = new Discord.Client();
const id ='/';
// Событие, которое срабатывает после успешного подключения бота к Discord
client.on('ready', () => {
  console.log(`Бот ${client.user.tag} успешно подключен к Discord!`);
});

// Событие, которое срабатывает при получении нового сообщения на сервере
client.on('message', (message) => {
  // Проверка, чтобы бот не отвечал сам себе или на сообщения других ботов
  if (message.author.bot) return;

 




  if (message.content === '/yagey') {
    // Создание ембеда
    const embed = new Discord.MessageEmbed()
      .setColor('#FF69B4') // Розовый цвет
      .setDescription('Я ПИДОРАС'); // Текст сообщения

    // Отправка ембеда в канал
    message.channel.send(embed);
  }











});

// Запуск бота
client.login('MTIxMDk2NTY4MjAxMTc2NjgwNA.G763lb.3yXdxnwllvEmgpVaEkFWJKab8jOGaT8pm4tCE0');