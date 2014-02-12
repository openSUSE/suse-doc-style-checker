<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:py="http://www.example.org/">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text()"/>

  <xsl:template match="/">
    <part>
      <part-title><xsl:apply-templates mode="part-title"/></part-title>
      <xsl:apply-templates/>
    </part>
  </xsl:template>

  <xsl:template name="createid">
    <xsl:param name="use-url-attribute" select="0"/>
    <xsl:param name="use-function-attribute" select="0"/>
    <xsl:param name="use-fileref-attribute" select="0"/>
    <xsl:param name="node" select="."/>

    <xsl:choose>
      <xsl:when test="$node/@id">
        <id><xsl:value-of select="$node/@id"/></id>
        <place>
          <line><xsl:value-of select="py:linenumber($node)"/></line>
        </place>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$node/title">
            <name><xsl:value-of select="normalize-space($node/title)"/></name>
          </xsl:when>
          <xsl:when test="$use-url-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@url)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@url), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@url)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:when test="$use-function-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@function)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@function), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@function)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:when test="$use-fileref-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@fileref)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@fileref), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@fileref)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:otherwise>
        </xsl:choose>
        <place>
          <xsl:if test="$node/ancestor::*[@id]">
            <withinid><xsl:value-of select="$node/ancestor::*[@id][1]/@id"/></withinid>
          </xsl:if>
          <line><xsl:value-of select="py:linenumber($node)"/></line>
        </place>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="safecharacters">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input,
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ?:;,!@#$%^§&amp;&lt;&gt;äàâãáåæÄÀÂÃÁÆÅçÇðÐèêéëËÉÈÊìîïíÍÏÌÎñÑòôõóöøœŒØÖÓÒÔÕùûüúÚÜÙÛýÿÝß©¢®þÞµ°[]“”{}|()= ',
      '')"/>
  </xsl:template>

  <xsl:template name="safecharacters-AZ">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '')"/>
  </xsl:template>

  <xsl:template name="safecharacters-special">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input,
      '?:;,!@#$%^§&amp;&lt;&gt;äàâãáåæÄÀÂÃÁÆÅçÇðÐèêéëËÉÈÊìîïíÍÏÌÎñÑòôõóöøœŒØÖÓÒÔÕùûüúÚÜÙÛýÿÝß©¢®þÞµ°[]“”{}|()= ',
      '')"/>
  </xsl:template>

</xsl:stylesheet>