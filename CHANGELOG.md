# Changelog

<!--next-version-placeholder-->

## v0.33.0 (2022-07-19)
### Feature
* **cpu:** Implement NOP operation ([#134](https://github.com/zeeps31/purenes/issues/134)) ([`442e7fa`](https://github.com/zeeps31/purenes/commit/442e7faabcd5cb197130371850c3bcb4a246081f))
* **cpu:** Implement RTI operation ([#133](https://github.com/zeeps31/purenes/issues/133)) ([`9de45fc`](https://github.com/zeeps31/purenes/commit/9de45fcc18c329ac3ee147a8a07b017c66341253))
* **cpu:** Implement RTS operation ([#132](https://github.com/zeeps31/purenes/issues/132)) ([`dd43ab0`](https://github.com/zeeps31/purenes/commit/dd43ab079f3c10d617c87bd74593cd62bae72a10))
* **cpu:** Implement comparison operations ([#131](https://github.com/zeeps31/purenes/issues/131)) ([`fca5dd5`](https://github.com/zeeps31/purenes/commit/fca5dd505ba94286b10610dd8b10377701b50160))
* **cpu:** Implement ROR operation ([#130](https://github.com/zeeps31/purenes/issues/130)) ([`de03d3a`](https://github.com/zeeps31/purenes/commit/de03d3a2fa380ef2e6130217891f74c1dcde9bf0))
* **cpu:** Implement LSR operation ([#129](https://github.com/zeeps31/purenes/issues/129)) ([`464df2d`](https://github.com/zeeps31/purenes/commit/464df2d6970a30bf18ec5a991333d6316dd2eb92))
* **cpu:** Implement EOR operation ([#128](https://github.com/zeeps31/purenes/issues/128)) ([`6663cfa`](https://github.com/zeeps31/purenes/commit/6663cfaca3ead5cbd60b1bbc6fe45bf154c7022a))
* **cpu:** Implement SBC operation ([#126](https://github.com/zeeps31/purenes/issues/126)) ([`86171bf`](https://github.com/zeeps31/purenes/commit/86171bf3a229967cf2204e0910c4a5cb83388bb8))
* **cpu:** Implement ADC operation ([#125](https://github.com/zeeps31/purenes/issues/125)) ([`62dcfa3`](https://github.com/zeeps31/purenes/commit/62dcfa3c4b74523e8229990f4a2ec0c38868cff6))
* **cpu:** Implement increment and decrement register operations ([#123](https://github.com/zeeps31/purenes/issues/123)) ([`fbcdd2c`](https://github.com/zeeps31/purenes/commit/fbcdd2c034e7a153dd5aa757d3d2551d6894a765))
* **cpu:** Implement INC operation ([#122](https://github.com/zeeps31/purenes/issues/122)) ([`2ce1fb7`](https://github.com/zeeps31/purenes/commit/2ce1fb7467580edcd62258f1e389c0e479af6852))
* **cpu:** Implement DEC operation ([#119](https://github.com/zeeps31/purenes/issues/119)) ([`ff43b8c`](https://github.com/zeeps31/purenes/commit/ff43b8cec4069371853f856086d4b5d25263b45e))
* **cpu:** Implement stack instructions ([#118](https://github.com/zeeps31/purenes/issues/118)) ([`8356ace`](https://github.com/zeeps31/purenes/commit/8356ace0cb57ff679a12b0d8a3125c6d67bacd74))
* **cpu:** Implement transfer instructions ([#117](https://github.com/zeeps31/purenes/issues/117)) ([`86888ac`](https://github.com/zeeps31/purenes/commit/86888ac110379b19b5ccddf1e60c08248e218ff5))
* **cpu:** Implement LDY operation ([#116](https://github.com/zeeps31/purenes/issues/116)) ([`c66645b`](https://github.com/zeeps31/purenes/commit/c66645b66ad401f38303cc67112b2f5703bdc7ed))
* **cpu:** Implement LDX operation ([#115](https://github.com/zeeps31/purenes/issues/115)) ([`46c57e6`](https://github.com/zeeps31/purenes/commit/46c57e6592389f0c1d731fbe7285a60efd45a280))
* **cpu:** Implement LDA operation ([#114](https://github.com/zeeps31/purenes/issues/114)) ([`1ad49b0`](https://github.com/zeeps31/purenes/commit/1ad49b06fb2fd5d19c38ffe81965713c03613f79))
* **cpu:** Implement STY operation ([#113](https://github.com/zeeps31/purenes/issues/113)) ([`cb25727`](https://github.com/zeeps31/purenes/commit/cb257272206c332fcc2f6e7d5fecd0a277fdb782))
* **cpu:** Implement STA ([#112](https://github.com/zeeps31/purenes/issues/112)) ([`3012fca`](https://github.com/zeeps31/purenes/commit/3012fca18a969469ac79a4613d841c6560672419))
* **cpu:** Implement ROL operation ([#110](https://github.com/zeeps31/purenes/issues/110)) ([`4ffd880`](https://github.com/zeeps31/purenes/commit/4ffd880ce21b8cd10250454c3001a1943a4178ad))
* **cpu:** Add BIT operation with absolute addressing ([#109](https://github.com/zeeps31/purenes/issues/109)) ([`d45440e`](https://github.com/zeeps31/purenes/commit/d45440ec4d9588ccb2c5eac0ebcd247ed1ed832a))
* **cpu:** Implement BIT operation ([#108](https://github.com/zeeps31/purenes/issues/108)) ([`c419cce`](https://github.com/zeeps31/purenes/commit/c419ccef250ce2e70d11fbee45df9e25374cfd02))
* **cpu:** Implement STX and y-indexed zero-page addressing ([#107](https://github.com/zeeps31/purenes/issues/107)) ([`61f6f4b`](https://github.com/zeeps31/purenes/commit/61f6f4b9e24bb2104b6f5b494d2148a4e5e102aa))
* **cpu:** Implement JMP operation and indirect addressing ([#106](https://github.com/zeeps31/purenes/issues/106)) ([`34700f7`](https://github.com/zeeps31/purenes/commit/34700f781dbf9b6d575171045ad1355ec5ef6600))
* **cpu:** Implement JSR operation ([#105](https://github.com/zeeps31/purenes/issues/105)) ([`779a543`](https://github.com/zeeps31/purenes/commit/779a54388f04dd1528dfaa72a4951fc1eb445ff8))
* **cpu:** Implement AND operation ([#103](https://github.com/zeeps31/purenes/issues/103)) ([`3a1b31c`](https://github.com/zeeps31/purenes/commit/3a1b31ccbfb877aeb0699b8f1dcbc21e4cc22984))
* **cpu:** Implement x-indexed absolute addressing ([#101](https://github.com/zeeps31/purenes/issues/101)) ([`bd63cd6`](https://github.com/zeeps31/purenes/commit/bd63cd6592f5f7daf17118466fac5131fc310a78))
* **cpu:** Implement y-indexed absolute addressing mode ([#99](https://github.com/zeeps31/purenes/issues/99)) ([`c0f4ec8`](https://github.com/zeeps31/purenes/commit/c0f4ec85727651125c808750b9932c2050f11e58))
* **cpu:** Implement flag set operations ([#98](https://github.com/zeeps31/purenes/issues/98)) ([`cd07aee`](https://github.com/zeeps31/purenes/commit/cd07aee772697e95b2763c6d57b4c7acce4c072f))
* **cpu:** Implement flag clear operations ([#97](https://github.com/zeeps31/purenes/issues/97)) ([`66b06b4`](https://github.com/zeeps31/purenes/commit/66b06b4c402b6eb6b99611bd5963193f6b4d6abb))
* **cpu:** Implement zero-page x-indexed addressing ([#96](https://github.com/zeeps31/purenes/issues/96)) ([`9be3020`](https://github.com/zeeps31/purenes/commit/9be30207e891f87fb94d9ee8deb2c9ed9fb6061c))
* **cpu:** Implement y-indexed indirect addressing mode ([#94](https://github.com/zeeps31/purenes/issues/94)) ([`08c0668`](https://github.com/zeeps31/purenes/commit/08c0668c1668cf7dec6c63502cf4ec49a67cd214))
* **cpu:** Implement branching instructions and relative addressing ([#93](https://github.com/zeeps31/purenes/issues/93)) ([`0dac7e6`](https://github.com/zeeps31/purenes/commit/0dac7e640ca461381229faec31123182ec3ad338))
* **cpu:** Implement absolute addressing mode ([#91](https://github.com/zeeps31/purenes/issues/91)) ([`4c47e83`](https://github.com/zeeps31/purenes/commit/4c47e839e2b505fd7eecdc9fbe5823c1ac2f5b9b))
* **cpu:** Implement accumulator addressing mode ([#90](https://github.com/zeeps31/purenes/issues/90)) ([`16c9819`](https://github.com/zeeps31/purenes/commit/16c98191ea238dc83d09078d3ffdd73c11ad5009))
* **cpu:** Implement immediate addressing mode ([#89](https://github.com/zeeps31/purenes/issues/89)) ([`3d234f5`](https://github.com/zeeps31/purenes/commit/3d234f51c946b8c7af33fc443a84f24115624f6c))
* **cpu:** Implement non-cycle-accurate clocking ([#88](https://github.com/zeeps31/purenes/issues/88)) ([`a57938d`](https://github.com/zeeps31/purenes/commit/a57938d07df6d37b4d36a4524b0f904b917e1fbd))
* **cpu:** Implement PHP operation ([#87](https://github.com/zeeps31/purenes/issues/87)) ([`7d3566b`](https://github.com/zeeps31/purenes/commit/7d3566b41f8f067fe8ba90fa10dd10b3d46ca791))
* **cpu:** Implement ASL operation ([#86](https://github.com/zeeps31/purenes/issues/86)) ([`52bbce4`](https://github.com/zeeps31/purenes/commit/52bbce4e0f09b099371b1c557e32ab703c4b0508))
* **cpu:** Implement zero-page addressing ([#84](https://github.com/zeeps31/purenes/issues/84)) ([`d01a11a`](https://github.com/zeeps31/purenes/commit/d01a11abd9b321b44c13db7f8a628160978ae78b))
* **cpu:** Implement ORA with X-indexed indirect addressing mode ([#81](https://github.com/zeeps31/purenes/issues/81)) ([`ee4d18e`](https://github.com/zeeps31/purenes/commit/ee4d18efc8d8fd413bc03327bb8c39073aeefe24))
* Implement BRK with implied addressing ([#79](https://github.com/zeeps31/purenes/issues/79)) ([`0d02170`](https://github.com/zeeps31/purenes/commit/0d021704ec6af4c78f670bcaf3133da23b20c5a2))
* **cpu:** Add CPUStatus (P) support and CPUReadOnlyValues ([#75](https://github.com/zeeps31/purenes/issues/75)) ([`c1cee8a`](https://github.com/zeeps31/purenes/commit/c1cee8a0ef0968636ea485dc60f064587567efcd))

### Documentation
* **cpu:** Add a topic guide related to the overflow flag ([#127](https://github.com/zeeps31/purenes/issues/127)) ([`b985d59`](https://github.com/zeeps31/purenes/commit/b985d59dd7f7b5a470e3df0d2ecfc7b889ed864f))

## v0.32.0 (2022-05-17)
### Feature
* **cartridge:** Introduce Cartridge class ([#72](https://github.com/zeeps31/purenes/issues/72)) ([`9f94b28`](https://github.com/zeeps31/purenes/commit/9f94b282f4c6a826ae80d67d5c11bf330fa7758d))

## v0.31.0 (2022-05-16)
### Feature
* **mappers:** Introduce Mapper and Mapper0 ([#71](https://github.com/zeeps31/purenes/issues/71)) ([`cba1e8e`](https://github.com/zeeps31/purenes/commit/cba1e8e45bda6d263970f658e37b02ab56a4aecd))

## v0.30.0 (2022-05-15)
### Feature
* **rom:** Introduce Rom class ([#70](https://github.com/zeeps31/purenes/issues/70)) ([`e7ce476`](https://github.com/zeeps31/purenes/commit/e7ce476bc4d949943eec2b21dbd4fa2fc7b0c271))

## v0.29.0 (2022-05-11)
### Feature
* **ppu:** Implement background pixel output ([#69](https://github.com/zeeps31/purenes/issues/69)) ([`0c7bb0e`](https://github.com/zeeps31/purenes/commit/0c7bb0ebdc763c36ed13f37ac8a30a43b2d184fc))

## v0.28.0 (2022-05-09)
### Feature
* **ppu:** Implement palette reads and writes ([#68](https://github.com/zeeps31/purenes/issues/68)) ([`e7367b3`](https://github.com/zeeps31/purenes/commit/e7367b3bbc0dcaf0685de89e93bd51a1c80829d3))

## v0.27.0 (2022-05-07)
### Feature
* **ppu:** Implement pattern table shift registers ([#64](https://github.com/zeeps31/purenes/issues/64)) ([`8218fed`](https://github.com/zeeps31/purenes/commit/8218fed23f12ac4c59dd3a71499d874b4e65ca1e))

## v0.26.0 (2022-05-07)
### Feature
* **ppu:** Implement attribute table shift registers ([#63](https://github.com/zeeps31/purenes/issues/63)) ([`13e061a`](https://github.com/zeeps31/purenes/commit/13e061aebde6a0302cce880da75087a5e5281ab1))

## v0.25.0 (2022-05-04)
### Feature
* **ppu:** Implement pattern table reads during a scanline cycle ([#62](https://github.com/zeeps31/purenes/issues/62)) ([`9c34c32`](https://github.com/zeeps31/purenes/commit/9c34c32b9b5d4d863ade648e13bfdaf3bb0bb2fa))

### Documentation
* **ppu:** Add documentation for attribute table address inference ([#60](https://github.com/zeeps31/purenes/issues/60)) ([`10535c4`](https://github.com/zeeps31/purenes/commit/10535c427218d58317147213341421e0d6c45975))

## v0.24.0 (2022-05-02)
### Feature
* **ppu:** Implement attribute table reads during a scanline cycle ([#59](https://github.com/zeeps31/purenes/issues/59)) ([`bddce50`](https://github.com/zeeps31/purenes/commit/bddce50544ec2c9b844a0d540b02c85670d9ca18))

### Documentation
* Improve CONTRIBUTING.md ([#57](https://github.com/zeeps31/purenes/issues/57)) ([`39a6075`](https://github.com/zeeps31/purenes/commit/39a60755d6432b901c0c7ac918e16bd9685aa141))
