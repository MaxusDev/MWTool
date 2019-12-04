const serialport = require('serialport');
const Readline = require('@serialport/parser-readline');

var portName = process.argv[2];

/*
  Port Connection
*/

var parser = new Readline({delimiter: "\n"});

function listPorts() {
  serialport.list().then(
    ports => {
    ports.forEach(port => {
      console.log(`${port.path}`);
    })},
    err => {
      console.error('Error listing ports', err);
    }
  )
}

var myPort = serialport(portName, { baudRate: 512000 });

myPort.pipe(parser);

parser.on('data', function(line) {
    console.log(line)  
})
