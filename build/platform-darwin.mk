include $(SRC_PATH)build/arch.mk
SHAREDLIB_DIR = $(PREFIX)/lib
SHAREDLIBSUFFIX = dylib
SHAREDLIBSUFFIXFULLVER=$(FULL_VERSION).$(SHAREDLIBSUFFIX)
SHAREDLIBSUFFIXMAJORVER=$(SHAREDLIB_MAJORVERSION).$(SHAREDLIBSUFFIX)
CURRENT_VERSION := 2.1.1
COMPATIBILITY_VERSION := 2.1.0
SHLDFLAGS = -dynamiclib -twolevel_namespace -undefined dynamic_lookup \
	-fno-common -headerpad_max_install_names -install_name \
	$(SHAREDLIB_DIR)/$(LIBPREFIX)$(PROJECT_NAME).$(SHAREDLIBSUFFIXMAJORVER)
SHARED = -dynamiclib
SHARED += -current_version $(CURRENT_VERSION) -compatibility_version $(COMPATIBILITY_VERSION)
CFLAGS += -Wall -fPIC -MMD -MP -fstack-protector-all -mmacosx-version-min=10.10

ifeq ($(ARCH), x86_64)
CFLAGS += --target=x86_64-apple-darwin17.7.0
LDFLAGS += --target=x86_64-apple-darwin17.7.0
else ifeq ($(ARCH), x86)
CFLAGS += --target=i386-apple-darwin17.7.0
LDFLAGS += --target=i386-apple-darwin17.7.0
else ifeq ($(ARCH), arm64)
CFLAGS += --target=arm64-apple-darwin20.5.0
LDFLAGS += --target=arm64-apple-darwin20.5.0
endif

ifeq ($(ASM_ARCH), x86)
ASMFLAGS += -DPREFIX
ifeq ($(ARCH), x86_64)
ASMFLAGS += -f macho64
else
ASMFLAGS += -f macho
LDFLAGS += -read_only_relocs suppress
endif
endif

